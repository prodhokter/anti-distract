import asyncio
import json
import logging
import threading

import websockets
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger(__name__)
PORT = 8765


class WSServer:
    def __init__(self):
        self._clients: set[WebSocketServerProtocol] = set()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._server = None
        self._ready = False

        self.on_blocked_tab: callable | None = None
        self.on_pause_request: callable | None = None
        self.on_start_request: callable | None = None
        self.on_stop_request: callable | None = None
        self.on_add_block_domain: callable | None = None

    @property
    def connection_count(self) -> int:
        return len(self._clients)

    @property
    def ready(self) -> bool:
        return self._ready

    def start(self):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="WSServer")
        self._thread.start()

    def stop(self):
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._serve())

    async def _serve(self):
        try:
            self._server = await websockets.serve(
                self._handler, "localhost", PORT, ping_interval=20, ping_timeout=10
            )
            self._ready = True
            logger.info(f"[WSServer] Listening on ws://localhost:{PORT}")
            await self._server.wait_closed()
        except OSError as e:
            logger.error(f"[WSServer] Bind gagal port {PORT}: {e}")

    async def _handler(self, ws: WebSocketServerProtocol):
        self._clients.add(ws)
        logger.info(f"[WSServer] Terhubung: {ws.remote_address}")
        try:
            async for raw in ws:
                try:
                    msg = json.loads(raw)
                    await self._handle_message(msg)
                except json.JSONDecodeError:
                    pass
        except websockets.ConnectionClosed:
            pass
        finally:
            self._clients.discard(ws)
            logger.info("[WSServer] Terputus")

    async def _handle_message(self, msg: dict):
        msg_type = msg.get("type")
        if msg_type == "blocked_tab":
            url = msg.get("url", "")
            hostname = msg.get("hostname", "")
            category = msg.get("category", "unknown")
            if self.on_blocked_tab:
                self.on_blocked_tab(url, hostname, category)
        elif msg_type == "pause_request":
            duration = msg.get("duration_m", 5)
            if self.on_pause_request:
                self.on_pause_request(duration)
        elif msg_type == "start_request":
            category = msg.get("category", "umum")
            deep_focus = msg.get("deep_focus", False)
            if self.on_start_request:
                self.on_start_request(category, deep_focus)
        elif msg_type == "stop_request":
            if self.on_stop_request:
                self.on_stop_request()
        elif msg_type == "add_block_domain":
            domain = msg.get("domain", "")
            if self.on_add_block_domain:
                self.on_add_block_domain(domain)

    def send_focus_state(self, active: bool, phase: str = "", remaining_s: int = 0,
                         cycle: int = 0, deep_focus: bool = False,
                         blocklist: list | None = None, categories: list | None = None):
        import core.repositories.settings_repo as sr
        daily_goal = int(sr.get_setting("daily_goal_minutes", "120"))
        self._broadcast(json.dumps({
            "type": "focus_state",
            "active": active,
            "phase": phase,
            "remaining_s": remaining_s,
            "cycle": cycle,
            "deep_focus": deep_focus,
            "blocklist": blocklist or [],
            "categories_blocked": categories or [],
            "daily_goal": daily_goal,
        }))

    def send_blocklist_update(self, blocklist: list, categories: list):
        self._broadcast(json.dumps({
            "type": "blocklist_update",
            "blocklist": blocklist,
            "categories": categories,
        }))

    def _broadcast(self, payload: str):
        if not self._loop or not self._clients:
            return
        asyncio.run_coroutine_threadsafe(self._do_broadcast(payload), self._loop)

    async def _do_broadcast(self, payload: str):
        dead = set()
        for ws in list(self._clients):
            try:
                await ws.send(payload)
            except websockets.ConnectionClosed:
                dead.add(ws)
        self._clients -= dead
