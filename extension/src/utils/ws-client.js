const WS_URL = "ws://localhost:8765";

let socket = null;
let reconnectTimer = null;
let listeners = new Map();

export function connect() {
  if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) return;

  try {
    socket = new WebSocket(WS_URL);
  } catch {
    scheduleReconnect();
    return;
  }

  socket.onopen = () => {
    clearTimeout(reconnectTimer);
    notifyListeners("connected", true);
  };

  socket.onmessage = (event) => {
    let msg;
    try { msg = JSON.parse(event.data); } catch { return; }
    notifyListeners("message", msg);
  };

  socket.onerror = () => scheduleReconnect();
  socket.onclose = () => {
    notifyListeners("disconnected", true);
    scheduleReconnect();
  };
}

function scheduleReconnect() {
  clearTimeout(reconnectTimer);
  reconnectTimer = setTimeout(connect, 4000);
}

export function send(msg) {
  if (socket?.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(msg));
  }
}

export function on(event, callback) {
  if (!listeners.has(event)) listeners.set(event, []);
  listeners.get(event).push(callback);
}

export function off(event, callback) {
  const cbs = listeners.get(event);
  if (cbs) {
    const idx = cbs.indexOf(callback);
    if (idx > -1) cbs.splice(idx, 1);
  }
}

function notifyListeners(event, data) {
  const cbs = listeners.get(event);
  if (cbs) cbs.forEach(fn => fn(data));
}

export function isConnected() {
  return socket?.readyState === WebSocket.OPEN;
}
