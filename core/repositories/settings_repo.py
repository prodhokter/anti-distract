import json
from typing import Any

from core.database import _conn, new_id


def get_setting(key: str, fallback: str = "") -> str:
    with _conn() as con:
        row = con.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else fallback


def set_setting(key: str, value: Any):
    with _conn() as con:
        con.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, str(value)),
        )


def get_blocklist() -> list[str]:
    raw = get_setting("blocklist", "[]")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


def set_blocklist(domains: list[str]):
    set_setting("blocklist", json.dumps(domains))


def get_blocked_categories() -> list[str]:
    raw = get_setting("blocked_categories", "[]")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


def set_blocked_categories(cats: list[str]):
    set_setting("blocked_categories", json.dumps(cats))
