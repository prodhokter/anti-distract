import datetime
import json
from core.repositories.session_repo import (
    add_xp as repo_add_xp,
    update_streak,
    increment_session_stats,
    get_user_progress,
    get_achievements,
    unlock_achievement,
    get_today_total_seconds,
    get_week_stats,
    get_peak_hours_data,
    get_plants,
    get_today_session_count,
    get_total_blocked_count,
    get_total_mood_entries,
    has_early_session,
    has_late_session,
)
from config.settings import XP_SESSION_BASE, XP_STREAK_MULTIPLIER, XP_BLOCK, ACHIEVEMENTS, LEVELS_XP


def calculate_session_xp(duration_s: int, streak: int, distraction_count: int) -> int:
    minutes = duration_s // 60
    base = XP_SESSION_BASE + minutes
    streak_bonus = int(base * (streak * XP_STREAK_MULTIPLIER))
    distraction_penalty = distraction_count * XP_BLOCK
    return max(0, base + streak_bonus + distraction_penalty)


def on_session_complete(duration_s: int, distraction_count: int = 0):
    user = get_user_progress()
    xp = calculate_session_xp(duration_s, user.get("current_streak", 0), distraction_count)

    result = repo_add_xp(xp)
    update_streak()
    increment_session_stats(duration_s // 60)

    earned = {"xp": xp, **result}

    achievements = check_achievements()
    earned["achievements"] = achievements

    return earned


def check_achievements() -> list[dict]:
    user = get_user_progress()
    unlocked = json.loads(user.get("achievements_json", "[]"))
    total_s = get_today_total_seconds()

    checks = []

    # Beginner
    if total_s > 0:
        checks.append("first_session")

    # Streak
    if user.get("current_streak", 0) >= 3:
        checks.append("streak_3")
    if user.get("current_streak", 0) >= 7:
        checks.append("streak_7")
    if user.get("current_streak", 0) >= 30:
        checks.append("streak_30")

    # Milestone
    if user.get("total_minutes", 0) >= 600:
        checks.append("total_10h")
    if user.get("total_minutes", 0) >= 6000:
        checks.append("total_100h")

    # Pomodoro
    if get_today_session_count() >= 10:
        checks.append("pomodoro_10")

    # Blocking
    if get_total_blocked_count() >= 100:
        checks.append("block_100")

    # Mood tracking
    if get_total_mood_entries() >= 10:
        checks.append("mood_tracker")

    # Time-based
    if has_early_session():
        checks.append("early_bird")
    if has_late_session():
        checks.append("night_owl")

    # Garden
    plants = get_plants()
    if len(plants) >= 5:
        checks.append("garden_5")

    new_unlocks = []
    for key in checks:
        if key not in unlocked:
            success, ach = unlock_achievement(key)
            if success:
                new_unlocks.append(ach)

    return new_unlocks
