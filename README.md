<h1 align="center">AntiDistract</h1>

<p align="center">
  <strong>Advanced Productivity Desktop App — Pomodoro Timer, AI Face Detection, Smart Website Blocking, and Virtual Garden Gamification</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python" />
  <img src="https://img.shields.io/badge/PyQt-6.8+-green.svg" alt="PyQt6" />
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="Platform" />
  <img src="https://img.shields.io/badge/license-MIT-purple.svg" alt="License" />
  <img src="https://img.shields.io/badge/extension-Chrome%20%7C%20Edge-yellow.svg" alt="Extension" />
</p>

---

## Daftar Isi

- [Overview](#overview)
- [Feature Comparison](#feature-comparison)
- [Quick Start](#quick-start)
- [Features](#features)
  - [Focus Mode](#focus-mode-pomodoro-20)
  - [AI Face Detection](#ai-face-detection-opencv-dnn)
  - [Smart Website Blocking](#smart-website-blocking)
  - [Virtual Garden](#virtual-garden)
  - [Gamification System](#gamification-system)
  - [Focus Analytics](#focus-analytics)
  - [Additional Features](#additional-features)
- [Face Detection Model](#face-detection-model)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Browser Extension Setup](#browser-extension-setup)
- [Auto-Start on Boot](#auto-start-on-boot)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)
- [Privacy](#privacy)
- [License](#license)

---

## Overview

AntiDistract is a desktop productivity application that combines **Pomodoro timer**, **AI face detection**, **smart website blocking**, and a **virtual garden gamification system** to help you stay focused. It pairs with a companion browser extension to block distracting websites during focus sessions.

**Made in Indonesia. 100% local. Zero cloud. Zero telemetry. Fully open source.**

Inspired by apps like Forest, Opal, and Cold Turkey — but entirely local, zero cloud dependency, and fully customizable.

### Compatibility

| Platform | Support | Notes |
|----------|---------|-------|
| Windows 10/11 | Full | Native Python + PyQt6, startup registry |
| macOS 12+ (Apple Silicon/Intel) | Full | OpenCV DNN works natively on both architectures |
| Linux (Ubuntu 22.04+, Debian 12+, Fedora 40+) | Full | Requires `libxcb-cursor0` and `libpulse0` |

---

## Feature Comparison

| Feature | AntiDistract | Forest | Cold Turkey | Opal |
|---------|:---:|:---:|:---:|:---:|
| Pomodoro Timer | Full FSM (pause/resume/skip) | Basic | None | Basic |
| AI Face Detection | OpenCV DNN (Caffe SSD) | None | None | None |
| Sleep Detection | dlib EAR (eye aspect ratio) | None | None | None |
| Category Blocking | 5 categories + per-schedule | None | Premium | iOS only |
| Virtual Garden | 5 plants, 5 stages, canvas | Trees only | None | None |
| XP & Achievements | 12 achievements, 50 levels | None | None | None |
| Sound Alarms | 5 tones, 7 profiles (WAV gen) | None | None | None |
| Soundscapes | 4 ambient sounds (rain, forest, etc.) | Premium | None | None |
| Habit Tracker | Daily/weekly/weekdays | None | None | None |
| Focus Analytics | Weekly, 30-day, heatmap | None | None | None |
| Motivation System | Quotes, milestones, celebrations | None | None | None |
| Data Export | CSV export (sessions + habits) | None | None | None |
| Browser Extension | Keyboard shortcuts, context menu | None | None | iOS only |
| Local Data | 100% offline (SQLite) | Cloud account | Local | Cloud |
| Free & Open Source | MIT License | Freemium | Freemium | Subscription |

---

## Quick Start

```bash
# Clone repository
git clone https://github.com/prodhokter/anti-distract.git
cd anti-distract

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

**Alternative install via pyproject.toml:**
```bash
pip install .
anti-distract
```

Face detection model (~10 MB) downloads automatically on first run to `~/.antidistract/models/`. Internet required only once.

---

## Features

### Focus Mode (Pomodoro 2.0)

Full state machine implementation: `IDLE → RUNNING → PAUSED → RUNNING`, with automatic phase transitions between **Work**, **Short Break**, and **Long Break**.

- Configurable work/break durations and cycles (1–120 minutes)
- Pause/Resume — missing in most Pomodoro apps
- **Deep Focus Mode** — locks controls, cannot pause or stop until session ends
- Skip phase button for manual control
- Auto-start next phase (toggleable)
- 7 session categories: Umum, Belajar, Coding, Menulis, Membaca, Desain, Riset
- Pre/post-session mood rating (1–5)
- Session notes
- Interruption and distraction counters

### AI Face Detection (OpenCV DNN)

Uses **OpenCV DNN Face Detector** with pre-trained Caffe SSD model — works on Python 3.9–3.14+ without binary compatibility issues. No MediaPipe dependency.

- Detects when you leave your screen
- Multi-face detection (detects if another person is in frame)
- Confidence scoring per detection
- Face presence logging for analytics
- Configurable away threshold (5–300 seconds)

**Three-level escalation system:**

| Level | Trigger | Response |
|-------|---------|----------|
| Level 1 | 50% of away threshold | Toast notification — gentle reminder |
| Level 2 | 100% of away threshold | Warning overlay + sound alert |
| Level 3 | 150% of away threshold | Critical fullscreen overlay + emergency alarm + 10-second countdown |

### Sleep/Drowsiness Detection (dlib EAR)

Optional sleep detection using **Eye Aspect Ratio (EAR)** via dlib's 68 facial landmark predictor. Detects when eyes stay closed beyond a configurable threshold.

- **EAR calculation**: 6 landmark points per eye (12 total), ratio of vertical to horizontal eye distances
- **Threshold**: EAR < 0.2 (eyes closed) for > `sleep_threshold_s` (default 10s)
- **Persistent alarm**: Continuous alarm until eyes re-open — does not auto-stop
- **Fallback**: If dlib not installed, sleep detection gracefully disables; face detection continues normally
- **Model**: `shape_predictor_68_face_landmarks.dat` auto-downloads to `~/.antidistract/models/`
- **Settings**: Enable/disable toggle + configurable threshold in Settings page

```bash
# Install dlib for sleep detection (optional)
pip install dlib>=19.24
```

### Persistent Alarm System

Three continuous alarm modes that **do not auto-stop** — they keep sounding until the condition is resolved:

| Mode | Trigger | Stop Condition |
|------|---------|----------------|
| Face Away (Level 2-3) | Away > 100% threshold | Face returns to camera |
| Sleep Detected | Eyes closed > threshold | Eyes re-open |
| Deep Focus Lock | Attempted pause in deep focus | Session ends |

Traditional alarms (session start/end, break reminders) still use fixed repeat counts.

### Motivation & Encouragement

Built-in motivation system to keep you engaged:

- **50+ Indonesian motivational quotes** — daily quote on dashboard, session-start quote on focus page
- **Milestone celebrations** — special notifications for streak milestones (3, 7, 14, 30, 60, 100 days), level-ups (every 5 levels), 100 hours total focus, 1000 tabs blocked
- **Gentle encouragement** — contextual messages when returning after distraction, completing sessions, checking habits
- **Weekly reflection** — positive-framing summary of weekly productivity

### Smart Website Blocking

Blocks distracting websites via the **companion browser extension** with category-based rules.

- **5 predefined categories** with curated domain lists:
  - **Media Sosial** — Facebook, Twitter, Instagram, TikTok, Reddit, LinkedIn
  - **Hiburan** — YouTube, Netflix, Twitch, Spotify, Disney+, Hulu
  - **Game** — Steam, Epic Games, Roblox, Discord, Twitch Gaming
  - **Berita** — CNN, BBC, Detik, Kompas, Tribunnews, Tempo
  - **Belanja** — Shopee, Tokopedia, Lazada, Amazon, Bukalapak
- Custom blocklist for individual domains
- **Schedule-based blocking** — auto-enable on specific days and time ranges (e.g., work hours)
- Real-time sync between desktop app and extension via WebSocket
- Blocked page with motivational quotes and countdown timer
- One-click "pause blocking" from extension popup (5-minute override)

### Virtual Garden

Every completed focus session "waters" your plants. Earn XP to grow them through 5 stages.

| Plant | Stages | XP Curve |
|-------|--------|----------|
| Pohon (Tree) | Seed → Sprout → Growing → Blooming → Full | 30/60/120/200 XP |
| Bunga (Flower) | Seed → Sprout → Growing → Blooming → Full | 20/40/80/150 XP |
| Kaktus (Cactus) | Seed → Sprout → Growing → Blooming → Full | 15/30/60/120 XP |
| Jamur (Mushroom) | Seed → Sprout → Growing → Blooming → Full | 10/20/40/80 XP |
| Tanaman (Herb) | Seed → Sprout → Growing → Blooming → Full | 15/30/60/100 XP |

- Interactive canvas with **QPainter-rendered plants** — animated sky, twinkling stars, floating particles (25 FPS)
- Click on any plant to view growth details, XP progress, and session count
- Full-grown plants can be "harvested" for achievement rewards
- Visual selection indicator with dashed border

### Gamification System

A complete XP and achievement engine to keep you motivated.

- **Levels (1–50+)**: XP-based progression with `100 × 1.5^(level-1)` curve
- **Streaks**: Current + longest streak tracking with consecutive day detection
- **12 Achievements**:
  - First Session, 3-Day Streak, 7-Day Streak, 30-Day Streak
  - Pomodoro Master (10 cycles in a day)
  - Dedication (10h total focus), Commitment (100h total focus)
  - Green Thumb (5 plants in garden)
  - Focus Guardian (100 tabs blocked)
  - Reflective (10 mood entries)
  - Early Bird (focus before 6 AM), Night Owl (focus after 11 PM)

**XP Sources:**
| Activity | XP Earned |
|----------|-----------|
| Complete session | 50 XP base + 10% per streak day multiplier |
| Block distraction | 2 XP per blocked tab |
| Complete habit | 10 XP per habit check |
| Complete daily intention | 30 XP |
| Log mood | 5 XP |

### Focus Analytics

Track your productivity patterns with data-driven insights.

- **Today's stats**: Focus time, away count, blocked tabs, current streak
- **Productivity Score**: Daily 0–100 score with A–E grading across 5 weighted categories
- **Weekly bar chart**: 7-day focus time comparison against daily goal
- **30-day trend line**: pyqtgraph-powered interactive line chart
- **Peak hours heatmap**: 24-hour productivity distribution to find your golden hours
- **Category breakdown**: Horizontal bar chart by session category
- **Achievement showcase**: 8-grid of unlocked/locked achievements

### Additional Features

- **Daily Intentions** — Set one main goal per day, check it off when complete
- **Habit Tracker** — Create habits with daily/weekly/weekdays frequency, checkbox completion, counts, integrates with XP system
- **Break Reminders** — 20-20-20 eye rest rule, stretch reminder (45m), hydration reminder (90m), all configurable
- **Sound Alarms** — 5 programmatically generated tone types (sine, dual-tone, emergency siren, bell, buzzer), 7 alarm profiles with persistent continuous mode
- **Soundscapes** — 4 built-in ambient sounds (rain, forest, cafe, white noise), auto-play on session start
- **Auto-Start Break/Work** — Optionally auto-advance to next phase without manual click
- **Data Export** — Export sessions and habits to CSV with date range filtering
- **Streak Freeze** — Protect your streak (3+ days) from one missed day, earnable again after 7 days
- **Keyboard Shortcuts** — `Ctrl+Shift+F` start focus, `Ctrl+Shift+P` pause/resume, `Ctrl+Shift+B` toggle blocking
- **Right-Click Context Menu** — "Blokir situs ini" and "Jeda blokir 5 menit" from any page
- **Dark/Light Theme** — Full QSS stylesheet with theme persistence, light mode default
- **System Tray** — Minimize to tray, quick-focus context menu (25/45/60 min), continue blocking in background
- **Build .exe** — `python build.py` generates standalone Windows executable via PyInstaller

---

## Face Detection Model

### How It Works

AntiDistract uses **OpenCV's DNN module** with a pre-trained Caffe SSD face detection model. On first run, the model files are downloaded automatically to `~/.antidistract/models/`:

| File | Size | Purpose |
|------|------|---------|
| `deploy.prototxt` | ~3 KB | Caffe model architecture definition |
| `res10_300x300_ssd_iter_140000.caffemodel` | ~10.7 MB | Pre-trained weights (300×300 input) |

### Why OpenCV DNN Instead of MediaPipe

| Aspect | OpenCV DNN (current) | MediaPipe (previous) |
|--------|---------------------|---------------------|
| Python version support | 3.9–3.14+ | 3.9–3.13 only (C++ bindings break on 3.14) |
| Cross-platform | Windows, macOS, Linux (no binary issues) | Limited by pre-built wheels |
| Model format | Caffe (standard, widely supported) | Proprietary TFLite |
| Detection quality | SSD-based, 0.5 confidence threshold | BlazeFace, comparable accuracy |
| Inference speed | ~3 FPS on CPU (480×360) | ~10 FPS on CPU |
| Installation | Already bundled with opencv-python | Separate ~200 MB package |

The switch prioritizes **compatibility and maintainability** over raw speed. 3 FPS is sufficient for presence detection (human reaction time is ~250ms).

### Offline Setup

If your machine has no internet access, download the model files manually:

```bash
mkdir -p ~/.antidistract/models

# Download prototxt
curl -o ~/.antidistract/models/deploy.prototxt \
  https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt

# Download caffemodel
curl -o ~/.antidistract/models/res10_300x300_ssd_iter_140000.caffemodel \
  https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel
```

Then transfer the files to the target machine's `~/.antidistract/models/` directory.

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                  Desktop App (PyQt6)                  │
│                                                      │
│  ┌──────────┐  ┌──────────────────────────────────┐ │
│  │  Sidebar │  │        Stacked Pages              │ │
│  │          │  │  Dashboard / Focus / Garden       │ │
│  │  6 pages │  │  Habits / Analytics / Settings    │ │
│  └──────────┘  └──────────────────────────────────┘ │
│                                                      │
│  ┌─────────────┐  ┌────────────┐  ┌───────────────┐ │
│  │ FocusService│  │ SoundAlarm │  │ BreakReminder │ │
│  │ (FSM)       │  │ (WAV gen)  │  │ (3 types)     │ │
│  └─────────────┘  └────────────┘  └───────────────┘ │
│                                                      │
│  ┌──────────────────────────────────────────────────┐│
│  │              Repositories (Data Layer)            ││
│  │  session_repo / settings_repo / SQLite            ││
│  └──────────────────────────────────────────────────┘│
│                                                      │
│  ┌──────────────┐         ┌─────────────────────────┐│
│  │ Face Monitor │         │   WebSocket Server      ││
│  │ (QThread)    │         │   (asyncio :8765)       ││
│  └──────────────┘         └───────────┬─────────────┘│
└───────────────────────────────────────┼──────────────┘
                                        │
                              WebSocket │ JSON
                                        │
┌───────────────────────────────────────┼──────────────┐
│                        Browser Extension (MV3)       │
│                                                      │
│  ┌─────────────────┐  ┌────────────┐  ┌───────────┐ │
│  │ Service Worker  │  │  Popup UI  │  │  Blocked  │ │
│  │ (background.js) │  │  (340px)   │  │  Page     │ │
│  └─────────────────┘  └────────────┘  └───────────┘ │
└──────────────────────────────────────────────────────┘
```

### Design Pattern

**Repository + Service + UI** — clean separation of concerns:

```
config/          → Constants, defaults, theme definitions
core/
  database.py    → SQLite connection manager, schema migrations
  repositories/  → Data access (SQL queries, no business logic)
  services/      → Business logic (state machines, calculations)
ui/
  app.py         → QApplication bootstrap, global stylesheet
  main_window.py → Shell window, event orchestration, escalation logic
  pages/         → Full-page views (6 pages)
  widgets/       → Reusable components (6 widgets)
face/            → Face detection thread (OpenCV DNN, QThread)
network/         → WebSocket server (asyncio event loop)
extension/       → Chrome/Edge extension (Manifest V3)
```

### Database

SQLite with WAL mode, foreign keys, and UUID primary keys. 11 tables:

`sessions`, `away_events`, `blocked_events`, `daily_intentions`, `habits`, `habit_completions`, `garden_plants`, `user_progress`, `achievements`, `settings`, `soundscapes`

All data stored locally at `~/.antidistract/antidistract.db`.

---

## Tech Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Desktop GUI | PyQt6 | 6.8+ | Full native UI, QSS theming, system tray |
| Face Detection | OpenCV DNN (Caffe SSD) | 4.10+ | AI face presence monitoring |
| Sleep Detection | dlib | 19.24+ | Eye Aspect Ratio (EAR), 68 landmarks (optional) |
| Computer Vision | OpenCV | 4.10+ | Camera capture, image processing |
| Charts | pyqtgraph | 0.13+ | Interactive analytics charts |
| WebSocket | websockets | 14+ | Real-time extension sync (bidirectional) |
| Database | SQLite 3 | Built-in | WAL mode, FK constraints, UUID PKs |
| Audio | wave + QMediaPlayer | Built-in | Programmatic WAV generation |
| Extension | Vanilla JS + Manifest V3 | — | Service worker, zero dependencies |
| Packaging | PyInstaller | 6+ | Single-file Windows executable |

---

## Installation

### Prerequisites

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.9 | 3.12+ |
| pip | 22.0+ | 24.0+ |
| Webcam | 720p | 1080p |
| Browser | Chrome 110+ / Edge 110+ | Latest |
| RAM | 4 GB | 8 GB |
| Disk | 500 MB | 1 GB |

### Option A: pip + requirements.txt (Recommended)

```bash
git clone https://github.com/prodhokter/anti-distract.git
cd anti-distract

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate       # Linux/macOS
# venv\Scripts\activate        # Windows

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

### Option B: pip install (via pyproject.toml)

```bash
git clone https://github.com/prodhokter/anti-distract.git
cd anti-distract
pip install .
anti-distract
```

For development (editable install):
```bash
pip install -e .
```

### Linux-specific Dependencies

On Linux, you may need additional system libraries:

```bash
# Ubuntu/Debian
sudo apt install libxcb-cursor0 libpulse0

# Fedora
sudo dnf install libxcb pulseaudio-libs

# Arch
sudo pacman -S libxcb pulseaudio
```

If you encounter `externally-managed-environment`:
```bash
pip install --break-system-packages -r requirements.txt
```

### macOS Notes

- OpenCV DNN works natively on both Apple Silicon (ARM64) and Intel (x86_64)
- Grant camera permission when prompted (System Preferences → Privacy → Camera)
- No additional system dependencies required

---

## Build Executable (Windows)

```bash
pip install pyinstaller
python build.py --onefile    # Single .exe di dist/AntiDistract.exe
python build.py --onedir     # Folder distribusi (startup lebih cepat)
python build.py --clean      # Bersihkan build cache dulu
```

Model face detection otomatis di-bundle ke dalam executable. Output di `dist/`.

---

## Browser Extension Setup

1. Open `chrome://extensions` in Chrome (or `edge://extensions` in Edge)
2. Enable **Developer mode** (toggle, top right)
3. Click **Load unpacked**
4. Select the `extension/` folder from this project
5. The extension auto-connects to the desktop app via WebSocket on `ws://localhost:8765`

### Verifying Extension Connection

1. Start the desktop app: `python main.py`
2. Click the extension icon in your browser toolbar
3. Popup shows connection status:
   - **Green pulsing dot** — Connected, focus state synced
   - **Red dot** — Not connected (start the desktop app first)
4. If not connecting: reload extension at `chrome://extensions`, check firewall settings

### Extension Permissions Explained

| Permission | Why Required |
|------------|-------------|
| `tabs` | Redirect blocked websites to the blocked page |
| `webNavigation` | Intercept navigation BEFORE page loads |
| `storage` | Persist blocklist and state locally |
| `alarms` | Timer for schedule-based blocking |
| `contextMenus` | Right-click "Blokir situs ini" on any page |
| `commands` | Keyboard shortcuts (Ctrl+Shift+F/P/B) |
| `<all_urls>` | Block any distracting domain |

All data stays local. No information leaves your browser.

---

## Auto-Start on Boot

Dua metode instalasi punya cara autostart berbeda:

| Metode Instalasi | Command Autostart | Kelebihan |
|------------------|-------------------|-----------|
| pip + requirements.txt | `cd /path/to/project && python main.py` | Path project fleksibel |
| pip install . (pyproject.toml) | `anti-distract` langsung | Command global, tidak perlu cd |

### Windows

**Metode A — pip + requirements.txt (script bawaan):**

```bash
# Install ke startup registry
python scripts/setup_autostart.py install

# Cek status
python scripts/setup_autostart.py status

# Hapus dari startup
python scripts/setup_autostart.py remove
```

Script otomatis detect `pythonw.exe` dari `sys.executable` dan path absolut `main.py`. Entry disimpan di registry `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`.

**Metode B — pip install . (pyproject.toml):**

Setelah `pip install .`, command `anti-distract` tersedia global. Tidak perlu script — cukup tambah shortcut `anti-distract` ke folder Startup:

1. Buka `shell:startup` (Win+R)
2. Buat shortcut baru → target: `anti-distract`
3. Atau buat file `.bat` di folder Startup:
   ```bat
   @echo off
   anti-distract
   ```

### Linux (GNOME/KDE/XFCE)

**Metode A — pip + requirements.txt:**
```bash
mkdir -p ~/.config/autostart

cat > ~/.config/autostart/antidistract.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=AntiDistract
Exec=bash -c "cd /path/to/anti-distract && python3 main.py"
Terminal=false
StartupNotify=false
X-GNOME-Autostart-enabled=true
EOF
```

**Metode B — pip install . (lebih simpel):**
```bash
cat > ~/.config/autostart/antidistract.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=AntiDistract
Exec=anti-distract
Terminal=false
StartupNotify=false
X-GNOME-Autostart-enabled=true
EOF
```

### macOS

**Metode A:**
```
osascript -e "tell application \"System Events\" to make login item at end with properties {path:\"/path/to/anti-distract/main.py\", hidden:true}"
```

**Metode B (lebih simpel):**
```
osascript -e "tell application \"System Events\" to make login item at end with properties {path:\"$(which anti-distract)\", hidden:true}"
```

Atau via GUI: **System Preferences → General → Login Items & Extensions** → klik **+** → pilih `anti-distract` dari `/usr/local/bin/` atau path venv.

### Catatan

- Jalankan aplikasi manual dulu sebelum daftarin ke startup — pastikan model face detection sudah terdownload (~11 MB ke `~/.antidistract/models/`)
- Aplikasi minimize ke system tray saat startup, tidak mengganggu desktop
- Face detection dan WebSocket server otomatis jalan di background
- **Metode B lebih direkomendasikan untuk autostart** — command simpel, tidak bergantung path project

---

## Project Structure

```
anti-distract/
├── main.py                       # Entry point
├── build.py                      # PyInstaller build script
├── pyproject.toml                # Project metadata, Python >=3.9
├── requirements.txt              # Python dependencies
├── assets/
│   └── icons/
│       └── logo.svg              # App icon (purple-pink gradient shield)
├── config/
│   ├── __init__.py
│   ├── settings.py               # Constants, defaults, enums, achievements
│   └── theme.py                  # Dark/Light theme colors, QSS builder, design tokens
├── core/
│   ├── __init__.py
│   ├── database.py               # SQLite connection, WAL mode, migrations
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── session_repo.py       # Sessions, habits, garden, achievements CRUD
│   │   └── settings_repo.py      # Key-value settings CRUD
│   └── services/
│       ├── __init__.py
│       ├── focus_service.py      # Pomodoro state machine (FSM)
│       ├── block_service.py      # Category/schedule blocking logic
│       ├── garden_service.py     # Plant growth, watering, harvesting
│       ├── gamification_service.py  # XP, levels, streaks, achievements
│       ├── break_service.py      # Break reminders, productivity scorer
│       ├── sound_service.py      # Programmatic WAV generation, persistent alarms
│       ├── motivation_service.py # Daily quotes, milestones, encouragement
│       └── export_service.py     # CSV export for sessions and habits
├── ui/
│   ├── __init__.py
│   ├── app.py                    # QApplication bootstrap, global stylesheet
│   ├── main_window.py            # Main window, event orchestration, escalation
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── dashboard_page.py     # Overview stats, weekly chart
│   │   ├── focus_page.py         # Pomodoro timer, controls, face status
│   │   ├── garden_page.py        # Virtual garden view
│   │   ├── habits_page.py        # Habit tracker + daily intention
│   │   ├── analytics_page.py     # Charts, heatmap, achievements grid, export button
│   │   └── settings_page.py      # All settings panels (sleep, auto-start, etc.)
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── garden_canvas.py      # QPainter garden renderer (25 FPS, theme-aware)
│   │   ├── timer_display.py      # Circular progress timer
│   │   ├── warning_overlay.py    # Fullscreen distraction overlay
│   │   ├── sidebar.py            # Navigation sidebar
│   │   ├── bar_chart.py          # Weekly bar chart widget
│   │   └── glass_card.py         # Glass morphism containers + helpers
│   └── styles/
│       └── __init__.py
├── face/
│   ├── __init__.py
│   └── face_monitor.py           # OpenCV DNN face detection + dlib sleep detection
├── network/
│   ├── __init__.py
│   └── ws_server.py              # asyncio WebSocket server (localhost:8765)
├── extension/                    # Chrome/Edge Extension (Manifest V3)
│   ├── manifest.json
│   ├── package.json
│   └── src/
│       ├── background.js         # Service worker, tab blocking, WS, shortcuts, context menu
│       ├── popup/                # Popup UI (340px, stats, goal bar, pause buttons)
│       ├── blocked/              # Blocked page with quotes, fixed countdown
│       └── utils/                # WebSocket client, storage helpers
├── scripts/
│   └── setup_autostart.py        # Windows startup registry manager
└── docs/                         # Full documentation
    ├── INSTALL.md
    ├── USAGE.md
    ├── ARCHITECTURE.md
    ├── EXTENSION.md
    └── DEVELOPMENT.md
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [Installation Guide](docs/INSTALL.md) | Step-by-step setup for all platforms |
| [User Guide](docs/USAGE.md) | Complete walkthrough of all features |
| [Architecture](docs/ARCHITECTURE.md) | Codebase structure, design patterns, data flow |
| [Browser Extension](docs/EXTENSION.md) | Extension internals, WebSocket protocol, permissions |
| [Development](docs/DEVELOPMENT.md) | Contributing guidelines, coding standards, building |

---

## Troubleshooting

### "No module named 'PyQt6'"
```bash
pip install PyQt6>=6.8.0
```

### Camera not detected
- Ensure no other application is using the webcam
- Check Device Manager (Windows) or `ls /dev/video*` (Linux)
- Face detection disables automatically if camera is unavailable — other features remain functional

### WebSocket port 8765 in use
```bash
# Windows
netstat -ano | findstr :8765

# Linux/macOS
lsof -i :8765
```
Kill the conflicting process or change `WS_PORT` in `config/settings.py`.

### Extension not connecting
1. Verify desktop app is running (`python main.py`)
2. Reload extension at `chrome://extensions`
3. Check extension console (right-click extension → Inspect)
4. Verify no firewall blocks `localhost:8765`

### Face detection model download fails
Download manually (see [Face Detection Model](#face-detection-model) section for URLs). Place files in `~/.antidistract/models/`.

### Performance issues
- Face detection runs at ~3 FPS by default — expected and sufficient for presence monitoring
- Disable Garden animation: set timer interval higher in `ui/widgets/garden_canvas.py`
- Extension blocking only activates during active focus sessions

### Linux: Qt platform plugin error
```bash
# Ubuntu/Debian
sudo apt install libxcb-cursor0 libpulse0

# Then run with offscreen fallback if no X server
QT_QPA_PLATFORM=offscreen python main.py
```

---

## Privacy

**100% local. Zero cloud. Zero telemetry.**

- All data stored in `~/.antidistract/` (SQLite database + model files)
- Camera feed processed entirely in-memory via OpenCV DNN — never written to disk
- WebSocket runs exclusively on `localhost:8765` — no external network access
- No analytics, no tracking, no accounts, no sign-up
- Browser extension stores blocklist in `chrome.storage.local` — not synced to Google account

---

## License

MIT License — see [LICENSE](LICENSE) file for details.

---

<p align="center">
  <sub>Built with Python, PyQt6, and OpenCV. Data stays local forever.</sub>
</p>
