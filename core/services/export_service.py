"""Data export service — CSV export for sessions and habits."""

import csv
import datetime
import os
from pathlib import Path

from core.repositories.session_repo import (
    get_week_stats, get_habits, get_today_habit_completions,
)


def _get_sessions_csv(days: int = 90):
    """Export session data as CSV rows."""
    rows = [["Tanggal", "Menit Fokus", "Jumlah Sesi"]]
    data = get_week_stats(days)
    for r in data:
        rows.append([r["date"], str(r["total_minutes"]), str(r.get("sessions", 1))])
    return rows


def _get_habits_csv():
    """Export habits data as CSV rows."""
    habits = get_habits(active_only=False)
    today = datetime.date.today().isoformat()
    completions = get_today_habit_completions()

    rows = [["Nama", "Frekuensi", "Aktif", "Selesai Hari Ini"]]
    for h in habits:
        rows.append([
            h["name"],
            h.get("frequency", "daily"),
            "Ya" if h.get("active", 1) else "Tidak",
            "Ya" if h["id"] in completions else "Tidak",
        ])
    return rows


def export_sessions(filepath: str | None = None, days: int = 90) -> str:
    """Export session data to CSV. Returns the file path."""
    if filepath is None:
        desktop = Path.home() / "Desktop"
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = str(desktop / f"antidistract_sessions_{ts}.csv")

    rows = _get_sessions_csv(days)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    return filepath


def export_habits(filepath: str | None = None) -> str:
    """Export habits data to CSV. Returns the file path."""
    if filepath is None:
        desktop = Path.home() / "Desktop"
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = str(desktop / f"antidistract_habits_{ts}.csv")

    rows = _get_habits_csv()
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    return filepath


def export_all(sessions_days: int = 90) -> dict:
    """Export both sessions and habits. Returns {sessions_path, habits_path}."""
    return {
        "sessions": export_sessions(days=sessions_days),
        "habits": export_habits(),
    }
