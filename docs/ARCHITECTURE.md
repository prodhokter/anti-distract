# Architecture

Dokumentasi arsitektur teknis AntiDistract — pattern, data flow, dan keputusan desain.

---

## Design Philosophy

### Prinsip Utama

1. **Local-first** — Semua data di SQLite lokal. Tidak ada cloud dependency.
2. **Separation of Concerns** — Repository → Service → UI, tidak boleh ada SQL di UI code.
3. **State Machine** — Pomodoro bukan spaghetti if-else, tapi FSM formal.
4. **Event-driven** — Komponen berkomunikasi via sinyal PyQt6 + WebSocket.
5. **Zero-config** — Database dan file suara dibuat otomatis saat startup.

### Pola Arsitektur

```
┌─────────────────────────────────────────────────┐
│                    UI Layer                      │
│  Pages (Dashboard, Focus, Garden, dll)          │
│  Widgets (Canvas, Timer, Overlay, Chart)        │
│  MainWindow (Orchestrator, event hub)           │
├─────────────────────────────────────────────────┤
│                  Service Layer                   │
│  FocusService (FSM)                             │
│  BlockService (Category + Schedule)             │
│  GardenService (Plant lifecycle)                │
│  GamificationService (XP + Achievements)        │
│  BreakService (Reminders + Scoring)             │
│  SoundService (WAV generation + persistent)     │
│  MotivationService (Quotes + Milestones)        │
│  ExportService (CSV export)                     │
├─────────────────────────────────────────────────┤
│                Repository Layer                  │
│  session_repo.py    settings_repo.py            │
│  (Data access, SQL queries only)                │
├─────────────────────────────────────────────────┤
│                 Data Layer                       │
│  SQLite (WAL mode, FK, UUID PK)                 │
│  ~/.antidistract/antidistract.db                │
└─────────────────────────────────────────────────┘
```

**Aturan ketat**: UI tidak pernah menyentuh SQL. Service tidak pernah menyentuh QWidget. Repository hanya berisi query.

---

## Component Deep Dive

### 1. FocusService — Pomodoro State Machine

```
                 ┌─────────┐
                 │  IDLE   │
                 └────┬────┘
                      │ start()
                      ▼
                 ┌─────────┐
          ┌──────│ RUNNING │◄──────┐
          │      └────┬────┘       │
          │ pause()   │  tick()    │ resume()
          │           ▼            │
          │      ┌─────────┐       │
          └─────►│ PAUSED  │───────┘
                 └─────────┘

Phase dalam RUNNING:
  WORK ──► SHORT_BREAK ──► WORK ──► ... ──► LONG_BREAK ──► WORK
```

**File**: `core/services/focus_service.py`

**Enums**:
- `State`: IDLE, RUNNING, PAUSED
- `Phase`: WORK, SHORT_BREAK, LONG_BREAK

**Key methods**:
| Method | Transisi |
|--------|----------|
| `configure(w, sb, lb, cycles)` | Set durasi |
| `start()` | IDLE → RUNNING (WORK) |
| `pause()` | RUNNING → PAUSED |
| `resume()` | PAUSED → RUNNING |
| `stop()` | Any → IDLE |
| `tick()` | +1 detik, cek phase transition |
| `skip_phase()` | WORK → BREAK atau BREAK → WORK |

**Design decision**: Kenapa state machine, bukan timer-based?
Karena FSM membuat semua state transisi eksplisit dan testable. Tidak ada "magic number" atau flag boolean `isWorking`/`isOnBreak`. Setiap state hanya punya transisi yang valid.

### 2. Face Detection Pipeline

```
┌──────────┐    ┌──────────────┐    ┌────────────┐
│  Webcam  │───►│  OpenCV DNN   │───►│  FaceMonitor │
│  (OpenCV)│    │  Face Detect  │    │  (QThread)   │
└──────────┘    └──────────────┘    └──────┬─────┘
                                           │ PyQt Signals
                                           ▼
                                    ┌──────────────┐
                                    │  MainWindow   │
                                    │  (Escalation  │
                                    │   Logic)      │
                                    └──────────────┘
```

**File**: `face/face_monitor.py`

**Mengapa OpenCV DNN, bukan Haar Cascade?**
- Akurasi lebih tinggi (confidence score 0-1)
- Multi-face detection built-in
- Lebih tahan terhadap variasi pencahayaan
- Model Caffe SSD, tidak ada binary compatibility issue (Python 3.9–3.14+)
- Model diunduh otomatis ke `~/.antidistract/models/` pada first run

**Model download mechanism**:
1. `FaceMonitor.run()` memanggil `_ensure_models()` sebelum inisialisasi detector
2. `_ensure_models()` cek apakah `deploy.prototxt` dan `caffemodel` sudah ada di `~/.antidistract/models/`
3. Jika belum, download via `urllib.request.urlretrieve()` dengan progress reporting
4. Model di-load sekali via `cv2.dnn.readNetFromCaffe()`, digunakan sepanjang session

**Thread safety**: FaceMonitor adalah `QThread` terpisah. Komunikasi hanya melalui PyQt signals (`status_changed`, `away_alert`, `face_returned`, `multi_face_detected`). Tidak ada shared state.

**Parameter**:
- Input resolusi: 300×300 (Caffe SSD input blob)
- Camera resolusi: 480×360 (cukup untuk face detection, rendah untuk CPU)
- Inference interval: ~300ms (~3 FPS via `time.sleep(0.3)`)
- Confidence threshold: 0.5
- Backend: DNN_BACKEND_DEFAULT, target: DNN_TARGET_CPU

### 3. Sleep Detection Pipeline (dlib EAR)

```
┌──────────┐    ┌──────────────┐    ┌──────────────────┐
│  Webcam  │───►│  dlib Face    │───►│  Eye Aspect Ratio │
│  (OpenCV)│    │  Landmarks    │    │  (EAR) Calculator  │
└──────────┘    └──────────────┘    └────────┬─────────┘
                                             │
                                             ▼
                                      ┌──────────────┐
                                      │  FaceMonitor   │
                                      │  sleep_detected│
                                      │  sleep_ended   │
                                      └──────┬───────┘
                                             │ PyQt Signals
                                             ▼
                                      ┌──────────────┐
                                      │  MainWindow   │
                                      │  (Continuous  │
                                      │   Alarm)      │
                                      └──────────────┘
```

**File**: `face/face_monitor.py`

**Dependency**: dlib (opsional). Jika tidak terinstall, sleep detection otomatis disabled — face detection tetap jalan normal.

**Algoritma EAR (Eye Aspect Ratio)**:
```
EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)

Dimana p1-p6 adalah 6 landmark points per mata:
  p1: left corner, p2: top-left, p3: top-right
  p4: right corner, p5: bottom-right, p6: bottom-left
```

- EAR > 0.2: mata terbuka (normal)
- EAR < 0.2: mata tertutup
- Mata tertutup > `sleep_threshold_s` (default 10 detik): trigger `sleep_detected`
- Mata terbuka kembali: trigger `sleep_ended`

**Model**: `shape_predictor_68_face_landmarks.dat` (~100 MB) auto-download ke `~/.antidistract/models/`.

**Parameter**:
- `sleep_threshold_s`: 10 (default, configurable 5-120 di settings)
- `sleep_detection_enabled`: True/False
- `HAS_DLIB`: Flag runtime untuk cek ketersediaan dlib

### 4. Persistent Alarm System

**File**: `core/services/sound_service.py`

Tiga mode alarm kontinu yang **tidak auto-stop** sampai kondisi resolved:

| Mode | Trigger | Stop Condition |
|------|---------|----------------|
| `away_critical` | Face away > 100% threshold | `face_returned` signal |
| `sleep_alarm` | Mata tertutup > sleep_threshold | `sleep_ended` signal |
| `deep_focus_lock` | Attempt pause in deep focus | Session ends |

**Implementasi**:
```python
def play_continuous(profile_key: str):
    """Loop tanpa batas via QTimer(repeat_count=-1)."""
    
def stop_all():
    """Stop semua continuous alarm yang sedang aktif."""
```

Continuous alarm menggunakan `_continuous_timers` dict (QTimer dengan `repeat_count=-1`) dan `_continuous_effects` dict (QSoundEffect). Method `is_continuous_active()` untuk cek state.

**Berbeda dengan alarm biasa**: Alarm sesi (start/end/break) tetap menggunakan `play()` dengan repeat count fixed. Hanya alarm yang terkait kehadiran user yang kontinu.

### 5. WebSocket Protocol

```
Desktop App ←─────── WebSocket (JSON) ───────→ Browser Extension
(localhost:8765)                               (Service Worker)
```

**File**: `network/ws_server.py`

**Message format**:

```json
// App → Extension: Focus state update
{
  "type": "focus_state",
  "active": true,
  "phase": "work",
  "remaining_s": 1500,
  "cycle": 3,
  "deep_focus": false,
  "blocklist": ["youtube.com", "twitter.com"],
  "categories_blocked": ["social_media", "entertainment"]
}

// App → Extension: Blocklist changed
{
  "type": "blocklist_update",
  "blocklist": ["..."],
  "categories": ["..."]
}

// Extension → App: Tab was blocked
{
  "type": "tab_blocked",
  "url": "https://youtube.com/watch?v=abc",
  "hostname": "youtube.com",
  "category": "entertainment"
}

// Extension → App: User requested pause
{
  "type": "pause_request",
  "duration_m": 5
}

// Extension → App: User requested start focus session
{
  "type": "start_request",
  "category": "umum",
  "deep_focus": false
}

// Extension → App: User requested stop focus session
{
  "type": "stop_request"
}

// Extension → App: Add domain to blocklist
{
  "type": "add_block_domain",
  "domain": "reddit.com"
}

// App → Extension: Daily goal included in focus_state
{
  "type": "focus_state",
  "active": true,
  "phase": "work",
  "remaining_s": 1500,
  "cycle": 3,
  "deep_focus": false,
  "blocklist": ["youtube.com"],
  "categories_blocked": ["social_media"],
  "daily_goal": 120
}
```

**Design decision**: Kenapa WebSocket, bukan chrome.storage polling?
WebSocket memberikan real-time sync. Begitu user mulai fokus, extension langsung tahu dalam milidetik. Polling chrome.storage akan delay 1+ detik.

### 6. Smart Blocking Logic

```
┌─────────────┐     ┌──────────────────┐
│  Blocklist   │     │  Active Schedule? │
│  (domains)   │     │  (time + days)    │
└──────┬──────┘     └────────┬─────────┘
       │                      │
       └──────────┬───────────┘
                  ▼
        ┌─────────────────┐
        │  get_all_block_  │
        │  domains()       │
        └────────┬────────┘
                 ▼
        ┌─────────────────┐
        │  is_blocked()    │
        │  (URL parser)    │
        └────────┬────────┘
                 ▼
        ┌─────────────────┐
        │  Extension       │
        │  webNavigation   │
        │  .onBeforeNavigate│
        └─────────────────┘
```

**File**: `core/services/block_service.py`

**Schedule check** (`is_schedule_active`):
1. Cek `schedule_enabled` flag
2. Cek hari ini ada di `active_days`
3. Cek current time antara `start_time` dan `end_time`
4. Support overnight schedule (22:00-06:00)

### 7. Gamification Pipeline

```
Session End
     │
     ▼
┌────────────────┐
│ calculate_xp() │──► base XP + streak bonus
└───────┬────────┘
        ▼
┌──────────────┐
│ add_xp()     │──► update total_xp, check level up
└───────┬──────┘
        ▼
┌───────────────────┐
│ check_achievements│──► compare stats vs criteria
└───────┬───────────┘
        ▼
┌────────────────┐
│ unlock_ach()   │──► push to achievements_json
└───────┬────────┘
        ▼
┌────────────────┐
│ water_plant()  │──► add XP to active plant
└───────┬────────┘
        ▼
┌────────────────┐
│ update_streak()│──► check consecutive days
└────────────────┘
```

**File**: `core/services/gamification_service.py`, `core/services/garden_service.py`

**XP Formula**:
```python
session_xp = XP_SESSION_BASE * (1 + XP_STREAK_MULTIPLIER * streak_days)
# XP_SESSION_BASE = 50
# XP_STREAK_MULTIPLIER = 0.1
# Contoh: streak 7 hari → 50 * (1 + 0.1*7) = 85 XP
```

**Level Curve**:
```python
LEVELS_XP[level] = int(100 * (1.5 ** (level - 1)))
# Level 1: 100 XP
# Level 5: 506 XP
# Level 10: 3844 XP
# Level 20: 221,683 XP
```

### 8. Motivation Service

**File**: `core/services/motivation_service.py`

Sistem motivasi dengan tiga komponen:

**Daily Quote**: 50+ kutipan motivasi Bahasa Indonesia. `get_daily_quote()` return quote berdasarkan hash tanggal — konsisten sepanjang hari.

**Milestone Detection**: `check_milestones()` membandingkan stats user vs thresholds:
- Streak milestones: 3, 7, 14, 30, 60, 100, 365 hari
- Level milestones: setiap 5 level
- Hour milestones: 100, 500, 1000 jam total fokus
- Block milestones: 1000, 5000 tab diblokir

**Encouragement Messages**: `get_random_encouragement(category)` return pesan kontekstual:
- `session_complete` — setelah selesai sesi
- `face_returned` — setelah kembali dari away
- `habit_check` — setelah centang habit
- `tab_blocked` — saat tab diblokir
- `break_time` — saat mulai istirahat

**Weekly Reflection**: `get_weekly_reflection(stats)` menghasilkan ringkasan mingguan dengan positive framing.

### 9. Export Service

**File**: `core/services/export_service.py`

Export data ke CSV:

```python
export_sessions(filepath, days=30)  # Export sesi ke CSV
export_habits(filepath)             # Export habit ke CSV
export_all()                        # Export keduanya
```

CSV sessions: date, start_time, end_time, duration_s, category, phase, mood_before, mood_after, distractions, xp_earned.
CSV habits: name, frequency, completion_dates, total_completions, active.

### 10. Garden Rendering

**File**: `ui/widgets/garden_canvas.py`

**Rendering order** (back to front):
1. Sky gradient + twinkling stars (QLinearGradient, 40 stars, sin-based alpha)
2. Sun with radial glow (QRadialGradient, 4x radius glow)
3. Ground gradient + grass line
4. Grass blades (QPainterPath quadTo, 60+ blades)
5. Floating particles (30 particles, upward drift)
6. Plants (5 drawing functions, stage-based)
7. Plant progress bars + labels
8. Selection indicator (dashed border)

**Animation**: QTimer 40ms (25 FPS) → `_animate()` → `update()` → `paintEvent()`

**Plant drawing** is type-dispatched:
- `_draw_tree()` — trunk + layered radial gradient canopies
- `_draw_flower()` — stem + petal circle + animated wobble
- `_draw_cactus()` — rounded rect body + arms + top flower
- `_draw_mushroom()` — stem + QPainterPath curved cap + spots
- `_draw_herb()` — multiple QPainterPath leaf blades

### 11. Sound Generation

**File**: `core/services/sound_service.py`

Semua suara digenerate secara programmatic — tidak ada file audio eksternal. Menggunakan modul `wave` + `math`:

| Tipe | Frekuensi | Durasi | Bentuk |
|------|-----------|--------|--------|
| Sine (soft chime) | 440 Hz | 0.5s | Pure sine wave |
| Dual Tone (alert) | 440 + 880 Hz | 1.0s | Two-tone sweep |
| Emergency | 800-1200 Hz sweep | 2.0s | Rising pitch siren |
| Buzzer | 200 Hz | 0.3s | Square wave approximation |
| Bell | 880 Hz | 0.8s | Decaying sine with harmonics |

**7 Alarm Profiles** (6 standard + continuous variants):
- `away_warning` — Soft chime (level 1)
- `away_critical` — Emergency siren, **continuous** (level 2-3, stops on face_returned)
- `sleep_alert` — Emergency siren, **continuous** (stops on sleep_ended)
- `tab_blocked` — Alert (tab blocked)
- `break_reminder` — Bell (break time)
- `focus_start` — Soft chime (session start)
- `focus_end` — Bell (session complete)
- `deep_focus_lock` — Buzzer, **continuous** (attempted pause in deep focus)

**Continuous vs Standard**:
- Standard: `play(profile, repeat=3)` — bunyi N kali lalu stop
- Continuous: `play_continuous(profile)` — loop tanpa batas, stop via `stop_all()` atau `stop_continuous(profile)`

### 12. Database Schema

**File**: `core/database.py`

**Tables** (8 utama + 3 referensi):

```
sessions
├── id (TEXT PK, UUID)
├── date, start_time, end_time
├── duration_s, planned_s
├── phase (work|short_break|long_break)
├── pomodoro_cycle, completed
├── interruptions, distraction_count
├── mood_before, mood_after, productivity
├── note, category, xp_earned
└── created_at

away_events
├── id, session_id (FK), timestamp, duration_s

blocked_events
├── id, session_id (FK), timestamp, url, hostname, category

daily_intentions
├── id, date (UNIQUE), title, note, completed

habits
├── id, name, description, icon, color
├── category, frequency, target_count
├── active, archived_at

habit_completions
├── id, habit_id (FK), date, count, note
└── UNIQUE(habit_id, date)

garden_plants
├── id, plant_type, name, stage, xp, xp_required
├── planted_date, last_watered, session_count
├── position_x, position_y

user_progress
├── id (singleton), total_xp, level, xp_to_next
├── current_streak, longest_streak, last_active_date
├── total_sessions, total_minutes, achievements_json
```

**Indexes**:
- `idx_sessions_date` — Query per tanggal
- `idx_sessions_category` — Query per kategori
- `idx_blocked_date` — Query blocked events per tanggal
- `idx_habit_completions_date` — Query habit completions per tanggal

---

## Thread Model

```
┌──────────────────────────────────────────┐
│              Main Thread (GUI)            │
│  PyQt6 event loop                        │
│  UI rendering, user input                │
│  FocusService.tick() via QTimer (1s)     │
│  BreakReminder.check() via QTimer (30s)  │
└──────────────────────────────────────────┘
         │                  ▲
         │ Signals          │ Signals
         ▼                  │
┌─────────────────┐  ┌──────────────────┐
│  FaceMonitor     │  │  WSServer Thread │
│  (QThread)       │  │  (asyncio loop)  │
│                  │  │                  │
│  Kamera capture  │  │  WebSocket I/O   │
│  OpenCV DNN inf.  │  │  JSON parse      │
│  Signal emit     │  │  _broadcast()    │
└─────────────────┘  └──────────────────┘
```

- Face detection di thread terpisah — tidak blocking UI
- WebSocket server di thread terpisah (asyncio event loop)
- Semua komunikasi cross-thread via PyQt signals (thread-safe)
- Tidak ada shared mutable state antar thread

---

## Key Design Decisions

### Kenapa SQLite, bukan file JSON?
- Concurrent read/write via WAL mode
- Foreign key integrity
- Query aggregation (SUM, GROUP BY) untuk analytics
- Schema migrations terstruktur
- Tidak perlu load seluruh data ke memori

### Kenapa UUID, bukan autoincrement ID?
- ID bisa digenerate tanpa round-trip ke database
- Tidak ada collision saat multiple writers
- Standard untuk distributed system (meski kita single-user)

### Kenapa WebSocket, bukan REST API?
- Real-time push tanpa polling
- Dua arah: app → extension dan extension → app
- Satu persistent connection — overhead rendah
- JSON format simple untuk kedua sisi

### Kenapa programmatic sound generation?
- Tidak perlu file audio terpisah
- Tidak ada masalah path/relative path
- Bisa digenerate adaptif (pitch, durasi, waveform)
- File WAV << 100KB, disimpan di temp directory

### Kenapa pyqtgraph, bukan matplotlib?
- pyqtgraph adalah native Qt widget — tidak ada bridge/render issue
- Lebih ringan (pure Python, no C++ matplotlib backend)
- Real-time update lebih cepat
- Cocok untuk embedded chart di aplikasi desktop

---

[Kembali ke README](../README.md)
