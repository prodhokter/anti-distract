import sqlite3
import json
import uuid
from pathlib import Path
from typing import Any

from config.settings import DB_PATH

SCHEMA_VERSION = 1


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(DB_PATH))
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA foreign_keys=ON")
    con.row_factory = sqlite3.Row
    return con


def new_id() -> str:
    return uuid.uuid4().hex[:12]


def init_db():
    with _conn() as con:
        con.executescript(_SCHEMA)
        _run_migrations(con)
        _seed_defaults(con)


def _run_migrations(con: sqlite3.Connection):
    version = con.execute(
        "SELECT value FROM settings WHERE key='schema_version'"
    ).fetchone()
    current = int(version[0]) if version else 0

    if current < 1:
        pass


def _seed_defaults(con: sqlite3.Connection):
    from config.settings import DEFAULT_SETTINGS, ACHIEVEMENTS

    for k, v in DEFAULT_SETTINGS.items():
        con.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (k, v),
        )

    cur = con.execute("SELECT COUNT(*) FROM achievements").fetchone()
    if cur[0] == 0:
        for a in ACHIEVEMENTS:
            con.execute(
                "INSERT OR IGNORE INTO achievements (key, name, description, icon, xp_reward, category) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (a["key"], a["name"], a["desc"], a["icon"], a["xp"], a["category"]),
            )

    cur = con.execute("SELECT COUNT(*) FROM soundscapes").fetchone()
    if cur[0] == 0:
        builtin = [
            ("rain",       "Hujan",       "rain.mp3",       "🌧️"),
            ("forest",     "Hutan",       "forest.mp3",     "🌲"),
            ("cafe",       "Kafe",        "cafe.mp3",       "☕"),
            ("whitenoise", "White Noise", "whitenoise.mp3", "📡"),
        ]
        for sid, name, path, icon in builtin:
            con.execute(
                "INSERT OR IGNORE INTO soundscapes (id, name, file_path, icon, is_builtin) "
                "VALUES (?, ?, ?, ?, 1)",
                (sid, name, path, icon),
            )

    cur = con.execute("SELECT COUNT(*) FROM user_progress").fetchone()
    if cur[0] == 0:
        con.execute(
            "INSERT INTO user_progress (id) VALUES ('singleton')"
        )


_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id               TEXT PRIMARY KEY,
    date             TEXT NOT NULL,
    start_time       TEXT NOT NULL,
    end_time         TEXT,
    duration_s       INTEGER DEFAULT 0,
    planned_s        INTEGER NOT NULL,
    phase            TEXT NOT NULL DEFAULT 'work',
    pomodoro_cycle   INTEGER DEFAULT 0,
    completed        INTEGER DEFAULT 0,
    interruptions    INTEGER DEFAULT 0,
    mood_before      INTEGER,
    mood_after       INTEGER,
    productivity     INTEGER,
    note             TEXT DEFAULT '',
    category         TEXT DEFAULT 'umum',
    distraction_count INTEGER DEFAULT 0,
    xp_earned        INTEGER DEFAULT 0,
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(date);
CREATE INDEX IF NOT EXISTS idx_sessions_category ON sessions(category);

CREATE TABLE IF NOT EXISTS away_events (
    id          TEXT PRIMARY KEY,
    session_id  TEXT,
    timestamp   TEXT NOT NULL,
    duration_s  REAL NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS blocked_events (
    id          TEXT PRIMARY KEY,
    session_id  TEXT,
    timestamp   TEXT NOT NULL,
    url         TEXT NOT NULL,
    hostname    TEXT NOT NULL,
    category    TEXT DEFAULT 'unknown',
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
CREATE INDEX IF NOT EXISTS idx_blocked_date ON blocked_events(date(timestamp));

CREATE TABLE IF NOT EXISTS daily_intentions (
    id          TEXT PRIMARY KEY,
    date        TEXT NOT NULL UNIQUE,
    title       TEXT NOT NULL,
    note        TEXT DEFAULT '',
    completed   INTEGER DEFAULT 0,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS habits (
    id           TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    description  TEXT DEFAULT '',
    icon         TEXT DEFAULT 'default',
    color        TEXT DEFAULT '#6c63ff',
    category     TEXT DEFAULT 'umum',
    frequency    TEXT NOT NULL DEFAULT 'daily',
    target_count INTEGER DEFAULT 1,
    active       INTEGER DEFAULT 1,
    archived_at  TEXT,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS habit_completions (
    id         TEXT PRIMARY KEY,
    habit_id   TEXT NOT NULL,
    date       TEXT NOT NULL,
    count      INTEGER DEFAULT 1,
    note       TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
    UNIQUE(habit_id, date)
);
CREATE INDEX IF NOT EXISTS idx_habit_completions_date ON habit_completions(date);

CREATE TABLE IF NOT EXISTS garden_plants (
    id              TEXT PRIMARY KEY,
    plant_type      TEXT NOT NULL,
    name            TEXT,
    stage           INTEGER DEFAULT 0,
    xp              INTEGER DEFAULT 0,
    xp_required     INTEGER NOT NULL,
    planted_date    TEXT NOT NULL,
    last_watered    TEXT,
    session_count   INTEGER DEFAULT 0,
    position_x      REAL DEFAULT 0.5,
    position_y      REAL DEFAULT 0.5,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS user_progress (
    id                TEXT PRIMARY KEY DEFAULT 'singleton',
    total_xp          INTEGER DEFAULT 0,
    level             INTEGER DEFAULT 1,
    xp_to_next        INTEGER DEFAULT 100,
    current_streak    INTEGER DEFAULT 0,
    longest_streak    INTEGER DEFAULT 0,
    last_active_date  TEXT,
    total_sessions    INTEGER DEFAULT 0,
    total_minutes     INTEGER DEFAULT 0,
    achievements_json TEXT DEFAULT '[]',
    created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS achievements (
    key         TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT NOT NULL,
    icon        TEXT NOT NULL,
    xp_reward   INTEGER DEFAULT 0,
    category    TEXT DEFAULT 'general'
);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS soundscapes (
    id         TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    file_path  TEXT NOT NULL,
    icon       TEXT DEFAULT '🎵',
    is_builtin INTEGER DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY
);
"""
