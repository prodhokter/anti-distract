import sys
from pathlib import Path

APP_NAME = "AntiDistract"
APP_VERSION = "2.0.0"
ORG_NAME = "prodhokter"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path.home() / ".antidistract"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "antidistract.db"
ASSETS_DIR = BASE_DIR / "assets"
SOUNDS_DIR = ASSETS_DIR / "sounds"

WS_HOST = "localhost"
WS_PORT = 8765

# ── Default settings ──
DEFAULT_SETTINGS = {
    "daily_goal_minutes": "120",
    "away_threshold_s": "30",
    "pomodoro_work_m": "25",
    "pomodoro_break_short_m": "5",
    "pomodoro_break_long_m": "15",
    "pomodoro_cycles_before_long": "4",
    "deep_focus_password": "",
    "face_detection_enabled": "1",
    "auto_start_break": "1",
    "auto_start_work": "0",
    "soundscape_volume": "0.5",
    "soundscape_auto_play": "1",
    "alarm_volume": "0.7",
    "alarm_muted": "0",
    "theme": "dark",
    "blocklist": '["youtube.com","tiktok.com","twitter.com","instagram.com","facebook.com","reddit.com"]',
    "blocked_categories": '["social_media","entertainment"]',
    "block_schedule_enabled": "0",
    "block_schedule_start": "08:00",
    "block_schedule_end": "17:00",
    "block_schedule_days": "1,2,3,4,5",
    "break_eye_enabled": "1",
    "break_eye_interval": "20",
    "break_stretch_enabled": "1",
    "break_stretch_interval": "45",
    "break_hydration_enabled": "1",
    "break_hydration_interval": "90",
}

# Blocking categories with predefined domains
BLOCK_CATEGORIES = {
    "social_media": {
        "label": "Media Sosial",
        "domains": [
            "facebook.com", "twitter.com", "x.com", "instagram.com",
            "tiktok.com", "reddit.com", "linkedin.com", "snapchat.com",
            "pinterest.com", "threads.net", "mastodon.social",
        ],
    },
    "entertainment": {
        "label": "Hiburan",
        "domains": [
            "youtube.com", "netflix.com", "disneyplus.com", "hulu.com",
            "twitch.tv", "vimeo.com", "dailymotion.com", "bilibili.com",
            "spotify.com", "9gag.com", "imgur.com",
        ],
    },
    "gaming": {
        "label": "Game",
        "domains": [
            "steampowered.com", "epicgames.com", "roblox.com",
            "minecraft.net", "twitch.tv", "discord.com",
        ],
    },
    "news": {
        "label": "Berita",
        "domains": [
            "cnn.com", "bbc.com", "nytimes.com", "detik.com",
            "kompas.com", "tribunnews.com", "liputan6.com",
            "cnbcindonesia.com", "tempo.co", "viva.co.id",
        ],
    },
    "shopping": {
        "label": "Belanja",
        "domains": [
            "shopee.co.id", "tokopedia.com", "lazada.co.id",
            "bukalapak.com", "blibli.com", "amazon.com",
            "zalora.co.id", "amazon.co.id",
        ],
    },
}

# Achievement definitions
ACHIEVEMENTS = [
    {"key": "first_session",  "name": "Langkah Pertama",   "desc": "Selesaikan sesi fokus pertama",        "icon": "👶", "xp": 50,  "category": "beginner"},
    {"key": "streak_3",       "name": "Konsisten!",        "desc": "3 hari berturut-turut fokus",          "icon": "🔥", "xp": 100, "category": "streak"},
    {"key": "streak_7",       "name": "Tak Terhentikan",   "desc": "7 hari berturut-turut fokus",          "icon": "⚡", "xp": 250, "category": "streak"},
    {"key": "streak_30",      "name": "Legenda Fokus",     "desc": "30 hari berturut-turut fokus",         "icon": "👑", "xp": 1000,"category": "streak"},
    {"key": "pomodoro_10",    "name": "Pomodoro Master",   "desc": "10 siklus Pomodoro dalam sehari",      "icon": "🍅", "xp": 150, "category": "pomodoro"},
    {"key": "total_10h",      "name": "Dedikasi",          "desc": "Total 10 jam fokus",                   "icon": "⏰", "xp": 200, "category": "milestone"},
    {"key": "total_100h",     "name": "Komitmen",          "desc": "Total 100 jam fokus",                  "icon": "💎", "xp": 1000,"category": "milestone"},
    {"key": "garden_5",       "name": "Jempol Hijau",      "desc": "Tanam 5 tanaman di garden",            "icon": "🌱", "xp": 200, "category": "garden"},
    {"key": "block_100",      "name": "Penjaga Fokus",     "desc": "Blokir 100 tab pengganggu",            "icon": "🛡️", "xp": 150, "category": "blocking"},
    {"key": "mood_tracker",   "name": "Reflektif",         "desc": "Catat mood 10 kali",                   "icon": "📝", "xp": 100, "category": "reflection"},
    {"key": "early_bird",     "name": "Early Bird",        "desc": "Sesi fokus sebelum jam 6 pagi",        "icon": "🌅", "xp": 300, "category": "special"},
    {"key": "night_owl",      "name": "Night Owl",         "desc": "Sesi fokus setelah jam 11 malam",      "icon": "🦉", "xp": 300, "category": "special"},
]

# Plant type definitions
PLANT_TYPES = {
    "tree":     {"type": "tree", "name": "Pohon",   "icon": "🌳", "stages": ["🌰", "🌱", "🪴", "🌿", "🌳"], "xp_per_stage": [30, 60, 120, 200]},
    "flower":   {"type": "flower", "name": "Bunga",   "icon": "🌸", "stages": ["🌰", "🌱", "🌿", "🌷", "🌸"], "xp_per_stage": [20, 40, 80, 150]},
    "cactus":   {"type": "cactus", "name": "Kaktus",  "icon": "🌵", "stages": ["🌰", "🌱", "🌿", "🪴", "🌵"], "xp_per_stage": [15, 30, 60, 120]},
    "mushroom": {"type": "mushroom", "name": "Jamur",   "icon": "🍄", "stages": ["🌰", "🌱", "🍄", "🍄‍🟫", "🍄"], "xp_per_stage": [10, 20, 40, 80]},
    "herb":     {"type": "herb", "name": "Tanaman", "icon": "🌿", "stages": ["🌰", "🌱", "🌿", "🪴", "🌿"], "xp_per_stage": [15, 30, 60, 100]},
}

# XP system
XP_SESSION_BASE = 50
XP_STREAK_MULTIPLIER = 0.1
XP_HABIT = 10
XP_INTENTION = 30
XP_MOOD = 5
XP_BLOCK = 2
LEVELS_XP = {lv: int(100 * (1.5 ** (lv - 1))) for lv in range(1, 51)}
