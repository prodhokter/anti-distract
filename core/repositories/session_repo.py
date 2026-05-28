import datetime
import json
from typing import Any

from core.database import _conn, new_id

# ── Sessions ──


def start_session(phase: str = "work", planned_s: int = 1500, category: str = "umum") -> str:
    sid = new_id()
    now = datetime.datetime.now()
    with _conn() as con:
        con.execute(
            """INSERT INTO sessions (id, date, start_time, phase, planned_s, category)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (sid, now.strftime("%Y-%m-%d"), now.isoformat(), phase, planned_s, category),
        )
    return sid


def end_session(
    session_id: str,
    duration_s: int,
    completed: bool = False,
    interruptions: int = 0,
    mood_before: int | None = None,
    mood_after: int | None = None,
    productivity: int | None = None,
    note: str = "",
    distraction_count: int = 0,
    xp_earned: int = 0,
):
    now = datetime.datetime.now()
    with _conn() as con:
        con.execute(
            """UPDATE sessions SET end_time=?, duration_s=?, completed=?,
               interruptions=?, mood_before=?, mood_after=?, productivity=?,
               note=?, distraction_count=?, xp_earned=?
               WHERE id=?""",
            (
                now.isoformat(), duration_s, 1 if completed else 0,
                interruptions, mood_before, mood_after, productivity,
                note, distraction_count, xp_earned, session_id,
            ),
        )


def get_today_total_seconds() -> int:
    today = datetime.date.today().isoformat()
    with _conn() as con:
        row = con.execute(
            "SELECT COALESCE(SUM(duration_s),0) FROM sessions WHERE date=? AND end_time IS NOT NULL",
            (today,),
        ).fetchone()
        return int(row[0])


def get_today_stats() -> dict[str, Any]:
    today = datetime.date.today().isoformat()
    with _conn() as con:
        session_row = con.execute(
            "SELECT COUNT(*) as count, COALESCE(SUM(duration_s),0) as total_s "
            "FROM sessions WHERE date=? AND end_time IS NOT NULL",
            (today,),
        ).fetchone()
        away_row = con.execute(
            "SELECT COUNT(*) FROM away_events WHERE timestamp LIKE ?",
            (today + "%",),
        ).fetchone()
        blocked_row = con.execute(
            "SELECT COUNT(*) FROM blocked_events WHERE date(timestamp)=?",
            (today,),
        ).fetchone()
    return {
        "sessions": session_row["count"],
        "total_seconds": int(session_row["total_s"]),
        "away_count": away_row[0],
        "blocked_count": blocked_row[0],
    }


def get_week_stats(days: int = 7) -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            """SELECT date,
                      ROUND(SUM(duration_s)/60.0, 1) AS total_minutes,
                      COUNT(*) AS sessions
               FROM sessions
               WHERE date >= date('now', '-' || ? || ' days')
                 AND end_time IS NOT NULL
               GROUP BY date ORDER BY date""",
            (days - 1,),
        ).fetchall()
    return [{"date": r["date"], "total_minutes": r["total_minutes"], "sessions": r["sessions"]} for r in rows]


def get_peak_hours_data(days: int = 30) -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            """SELECT CAST(strftime('%H', start_time) AS INTEGER) as hour,
                      COUNT(*) as session_count,
                      SUM(duration_s)/60.0 as total_minutes
               FROM sessions
               WHERE date >= date('now', '-' || ? || ' days')
                 AND end_time IS NOT NULL
               GROUP BY hour ORDER BY hour""",
            (days,),
        ).fetchall()
    return [{"hour": r["hour"], "sessions": r["session_count"], "total_minutes": r["total_minutes"]} for r in rows]


def get_focus_trend(days: int = 30) -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            """SELECT date, ROUND(SUM(duration_s)/60.0, 1) AS total_minutes
               FROM sessions
               WHERE date >= date('now', '-' || ? || ' days')
                 AND end_time IS NOT NULL
               GROUP BY date ORDER BY date""",
            (days,),
        ).fetchall()
    return [{"date": r["date"], "total_minutes": r["total_minutes"]} for r in rows]


def get_category_stats(days: int = 30) -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            """SELECT COALESCE(category, 'umum') as category,
                      ROUND(SUM(duration_s)/60.0, 1) AS total_minutes,
                      COUNT(*) as session_count
               FROM sessions
               WHERE date >= date('now', '-' || ? || ' days')
                 AND end_time IS NOT NULL
               GROUP BY category ORDER BY total_minutes DESC""",
            (days,),
        ).fetchall()
    return [{"category": r["category"], "total_minutes": r["total_minutes"], "session_count": r["session_count"]} for r in rows]


# ── Away Events ──


def log_away(duration_s: float, session_id: str | None = None):
    with _conn() as con:
        con.execute(
            "INSERT INTO away_events (id, session_id, timestamp, duration_s) VALUES (?, ?, ?, ?)",
            (new_id(), session_id, datetime.datetime.now().isoformat(), duration_s),
        )


# ── Blocked Events ──


def log_blocked(url: str, hostname: str, category: str = "unknown", session_id: str | None = None):
    with _conn() as con:
        con.execute(
            "INSERT INTO blocked_events (id, session_id, timestamp, url, hostname, category) VALUES (?, ?, ?, ?, ?, ?)",
            (new_id(), session_id, datetime.datetime.now().isoformat(), url, hostname, category),
        )


# ── Daily Intentions ──


def get_today_intention() -> dict | None:
    today = datetime.date.today().isoformat()
    with _conn() as con:
        row = con.execute(
            "SELECT * FROM daily_intentions WHERE date=?",
            (today,),
        ).fetchone()
    return dict(row) if row else None


def set_daily_intention(title: str, note: str = "") -> str:
    today = datetime.date.today().isoformat()
    iid = new_id()
    with _conn() as con:
        con.execute(
            "INSERT OR REPLACE INTO daily_intentions (id, date, title, note) VALUES (?, ?, ?, ?)",
            (iid, today, title, note),
        )
    return iid


def complete_today_intention():
    today = datetime.date.today().isoformat()
    with _conn() as con:
        con.execute(
            "UPDATE daily_intentions SET completed=1 WHERE date=?",
            (today,),
        )


# ── Habits ──


def get_habits(active_only: bool = True) -> list[dict]:
    with _conn() as con:
        if active_only:
            rows = con.execute(
                "SELECT * FROM habits WHERE active=1 AND archived_at IS NULL ORDER BY created_at"
            ).fetchall()
        else:
            rows = con.execute(
                "SELECT * FROM habits ORDER BY created_at"
            ).fetchall()
    return [dict(r) for r in rows]


def create_habit(name: str, frequency: str = "daily", target_count: int = 1,
                 category: str = "umum", icon: str = "default", color: str = "#6c63ff",
                 description: str = "") -> str:
    hid = new_id()
    with _conn() as con:
        con.execute(
            """INSERT INTO habits (id, name, description, icon, color, category, frequency, target_count)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (hid, name, description, icon, color, category, frequency, target_count),
        )
    return hid


def toggle_habit(habit_id: str, date_str: str | None = None) -> bool:
    date_str = date_str or datetime.date.today().isoformat()
    with _conn() as con:
        existing = con.execute(
            "SELECT id, count FROM habit_completions WHERE habit_id=? AND date=?",
            (habit_id, date_str),
        ).fetchone()
        if existing:
            con.execute(
                "DELETE FROM habit_completions WHERE id=?",
                (existing["id"],),
            )
            return False
        else:
            con.execute(
                "INSERT INTO habit_completions (id, habit_id, date) VALUES (?, ?, ?)",
                (new_id(), habit_id, date_str),
            )
            return True


def get_today_habit_completions() -> set[str]:
    today = datetime.date.today().isoformat()
    with _conn() as con:
        rows = con.execute(
            "SELECT habit_id FROM habit_completions WHERE date=?",
            (today,),
        ).fetchall()
    return {r["habit_id"] for r in rows}


# ── Garden ──


def get_plants() -> list[dict]:
    with _conn() as con:
        rows = con.execute("SELECT * FROM garden_plants ORDER BY created_at").fetchall()
    return [dict(r) for r in rows]


def plant_seed(plant_type: str, xp_required: int, position_x: float = 0.5, position_y: float = 0.5,
               name: str | None = None) -> str:
    pid = new_id()
    today = datetime.date.today().isoformat()
    with _conn() as con:
        con.execute(
            """INSERT INTO garden_plants (id, plant_type, name, xp_required, planted_date, position_x, position_y)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (pid, plant_type, name, xp_required, today, position_x, position_y),
        )
    return pid


def water_plant(plant_id: str, xp_amount: int) -> dict | None:
    today = datetime.date.today().isoformat()
    with _conn() as con:
        plant = con.execute("SELECT * FROM garden_plants WHERE id=?", (plant_id,)).fetchone()
        if not plant:
            return None

        new_xp = plant["xp"] + xp_amount
        new_stage = plant["stage"]
        xp_needed = plant["xp_required"]

        if new_xp >= xp_needed and new_stage < 4:
            new_stage += 1
            new_xp = new_xp - xp_needed
            from config.settings import PLANT_TYPES
            pt = PLANT_TYPES.get(plant["plant_type"])
            if pt and new_stage < len(pt["xp_per_stage"]):
                xp_needed = pt["xp_per_stage"][new_stage]
            else:
                xp_needed = xp_needed * 2

        con.execute(
            """UPDATE garden_plants SET xp=?, stage=?, xp_required=?, last_watered=?, session_count=session_count+1
               WHERE id=?""",
            (new_xp, new_stage, xp_needed, today, plant_id),
        )
    return {"stage": new_stage, "xp": new_xp, "xp_required": xp_needed, "leveled_up": new_stage > plant["stage"]}


def get_garden_stats() -> dict:
    with _conn() as con:
        total = con.execute("SELECT COUNT(*) FROM garden_plants").fetchone()[0]
        full = con.execute("SELECT COUNT(*) FROM garden_plants WHERE stage=4").fetchone()[0]
    return {"total_plants": total, "full_grown": full}


# ── User Progress (Gamification) ──


def get_user_progress() -> dict:
    with _conn() as con:
        row = con.execute("SELECT * FROM user_progress WHERE id='singleton'").fetchone()
    return dict(row) if row else {}


def add_xp(amount: int) -> dict:
    with _conn() as con:
        user = dict(con.execute("SELECT * FROM user_progress WHERE id='singleton'").fetchone())
        new_xp = user["total_xp"] + amount
        level = user["level"]
        xp_to_next = user["xp_to_next"]

        leveled_up = False
        while new_xp >= xp_to_next:
            new_xp -= xp_to_next
            level += 1
            xp_to_next = int(100 * (1.5 ** (level - 1)))
            leveled_up = True

        con.execute(
            "UPDATE user_progress SET total_xp=?, level=?, xp_to_next=? WHERE id='singleton'",
            (new_xp, level, xp_to_next),
        )
    return {"total_xp": new_xp, "level": level, "xp_to_next": xp_to_next, "leveled_up": leveled_up}


def update_streak():
    today = datetime.date.today().isoformat()
    with _conn() as con:
        user = dict(con.execute("SELECT * FROM user_progress WHERE id='singleton'").fetchone())
        last = user.get("last_active_date") or ""

        if last == today:
            return

        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        if last == yesterday:
            new_streak = user["current_streak"] + 1
        else:
            new_streak = 1

        longest = max(user["longest_streak"], new_streak)
        con.execute(
            "UPDATE user_progress SET current_streak=?, longest_streak=?, last_active_date=? WHERE id='singleton'",
            (new_streak, longest, today),
        )


def increment_session_stats(minutes: int):
    with _conn() as con:
        con.execute(
            "UPDATE user_progress SET total_sessions=total_sessions+1, total_minutes=total_minutes+? WHERE id='singleton'",
            (minutes,),
        )


def get_achievements() -> list[dict]:
    with _conn() as con:
        rows = con.execute("SELECT * FROM achievements ORDER BY category").fetchall()
    return [dict(r) for r in rows]


def get_today_session_count() -> int:
    """Count completed session cycles today."""
    today = datetime.date.today().isoformat()
    with _conn() as con:
        row = con.execute(
            "SELECT COUNT(*) FROM sessions WHERE date=? AND end_time IS NOT NULL",
            (today,),
        ).fetchone()
    return int(row[0])


def get_total_blocked_count() -> int:
    """Count total blocked events across all time."""
    with _conn() as con:
        row = con.execute("SELECT COUNT(*) FROM blocked_events").fetchone()
    return int(row[0])


def get_total_mood_entries() -> int:
    """Count sessions where mood was logged."""
    with _conn() as con:
        row = con.execute(
            "SELECT COUNT(*) FROM sessions WHERE (mood_before IS NOT NULL) OR (mood_after IS NOT NULL)"
        ).fetchone()
    return int(row[0])


def has_early_session() -> bool:
    """Check if any session ended before 6 AM."""
    with _conn() as con:
        row = con.execute(
            "SELECT COUNT(*) FROM sessions WHERE end_time IS NOT NULL AND CAST(strftime('%H', end_time) AS INTEGER) < 6"
        ).fetchone()
    return int(row[0]) > 0


def has_late_session() -> bool:
    """Check if any session ended after 11 PM."""
    with _conn() as con:
        row = con.execute(
            "SELECT COUNT(*) FROM sessions WHERE end_time IS NOT NULL AND CAST(strftime('%H', end_time) AS INTEGER) >= 23"
        ).fetchone()
    return int(row[0]) > 0


def unlock_achievement(key: str) -> tuple[bool, dict | None]:
    with _conn() as con:
        user = dict(con.execute("SELECT * FROM user_progress WHERE id='singleton'").fetchone())
        unlocked = json.loads(user.get("achievements_json", "[]"))
        if key in unlocked:
            return False, None

        unlocked.append(key)
        con.execute(
            "UPDATE user_progress SET achievements_json=? WHERE id='singleton'",
            (json.dumps(unlocked),),
        )

        ach = dict(con.execute("SELECT * FROM achievements WHERE key=?", (key,)).fetchone())
    return True, ach
