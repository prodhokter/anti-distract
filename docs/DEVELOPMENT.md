# Development Guide

Panduan untuk developer yang ingin berkontribusi atau memodifikasi AntiDistract.

---

## Development Setup

### Prasyarat

- Python 3.9+ (kompatibel hingga 3.14+)
- Git
- Chrome atau Edge browser (untuk testing extension)
- Webcam (untuk testing face detection)
- Code editor (VS Code direkomendasikan)

### Clone & Setup

```bash
git clone https://github.com/prodhokter/anti-distract.git
cd anti-distract

# Virtual environment
python -m venv venv
source venv/bin/activate       # Linux/macOS
# venv\Scripts\activate        # Windows

# Install dependencies
pip install -r requirements.txt

# Atau editable install (untuk development):
pip install -e .

# Jalankan
python main.py
```

### Struktur Project

Lihat [ARCHITECTURE.md](ARCHITECTURE.md) untuk penjelasan detail setiap komponen.

---

## Python Version Compatibility

AntiDistract didesain untuk kompatibel dengan **Python 3.9 hingga 3.14+**. Keputusan desain utama untuk mencapai ini:

### Face Detection: OpenCV DNN (bukan MediaPipe)

MediaPipe menggunakan compiled C++ bindings yang tidak tersedia untuk Python 3.14+. OpenCV DNN (`cv2.dnn`) adalah pure C++ module yang sudah di-bundle dengan `opencv-python` — kompatibel di semua versi Python.

**Testing kompatibilitas:**
```bash
# Cek import di versi Python yang berbeda
python3.9 -c "from face import FaceMonitor; print('3.9 OK')"
python3.10 -c "from face import FaceMonitor; print('3.10 OK')"
python3.11 -c "from face import FaceMonitor; print('3.11 OK')"
python3.12 -c "from face import FaceMonitor; print('3.12 OK')"
python3.13 -c "from face import FaceMonitor; print('3.13 OK')"
python3.14 -c "from face import FaceMonitor; print('3.14 OK')"
```

### Model File

Model Caffe SSD (`deploy.prototxt` + `res10_300x300_ssd_iter_140000.caffemodel`) diunduh otomatis saat FaceMonitor pertama kali dijalankan. File disimpan di `~/.antidistract/models/`.

Untuk development offline, download model manual:
```bash
mkdir -p ~/.antidistract/models
curl -o ~/.antidistract/models/deploy.prototxt \
  https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt
curl -o ~/.antidistract/models/res10_300x300_ssd_iter_140000.caffemodel \
  https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel
```

### pyproject.toml

Project mendukung instalasi via `pip install .` (PEP 621). File `pyproject.toml` mendefinisikan:
- `requires-python = ">=3.9"`
- Dependencies (sinkron dengan `requirements.txt`)
- Build system (`setuptools`)
- Package discovery (`config*`, `core*`, `face*`, `network*`, `ui*`)

---

## Coding Standards

### Python

- **Type hints** untuk semua fungsi publik
- **PEP 8** — 4 spaces, 100 char line limit
- **Docstrings** untuk service functions (satu baris)
- **No magic numbers** — gunakan konstanta dari `config/settings.py`
- **Repository pattern**: Semua akses database via `repositories/`, tidak ada SQL di UI code

```python
# Good
def start_session(phase: str = "work", planned_s: int = 1500, category: str = "umum") -> str:
    sid = new_id()
    now = datetime.datetime.now()
    ...

# Bad
def start_session(phase="work", planned_s=1500):
    id = str(uuid4())
    ...
```

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Files | snake_case | `focus_service.py` |
| Classes | PascalCase | `FocusService` |
| Functions | snake_case | `start_session()` |
| Constants | UPPER_SNAKE | `XP_SESSION_BASE` |
| Private methods | `_prefix` | `_advance_phase()` |
| UI widgets | `_prefix` instance var | `self._btn_start` |

### UI Code

- Setiap halaman adalah subclass `QWidget`
- Widget reusable di `ui/widgets/`
- Style via QSS stylesheet (tidak inline `setStyleSheet` kecuali dynamic)
- Gunakan `make_label()` helper dari `glass_card.py` untuk konsistensi
- Theme colors via `config.theme.CURRENT`

```python
# Good
from config.theme import CURRENT as C
label = make_label("Judul", 22, bold=True)

# Bad
label = QLabel("Judul")
label.setStyleSheet("font-size: 22px; font-weight: bold;")
```

### Services

- Service adalah pure Python — tidak ada PyQt imports
- State machine untuk logic kompleks (jangan if-else berantai)
- Method kecil (<30 baris), satu tanggung jawab

---

## Adding New Features

### New Page

1. Buat file di `ui/pages/`
2. Subclass `QWidget`
3. Implement `_build()` untuk layout
4. Tambahkan navigasi di `ui/widgets/sidebar.py`
5. Tambahkan page ke `QStackedWidget` di `main_window.py`

```python
# ui/pages/my_page.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from ui.widgets.glass_card import make_label

class MyPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.addWidget(make_label("Halaman Baru", 22, bold=True))

    def refresh(self):
        pass  # Dipanggil setiap kali page jadi visible
```

### New Service

1. Buat file di `core/services/`
2. Pure Python class — tidak import PyQt6
3. Public API dengan type hints
4. Jika perlu data, gunakan repository functions

```python
# core/services/my_service.py
from core.repositories.session_repo import get_today_stats

def calculate_my_metric() -> int:
    stats = get_today_stats()
    return stats["total_seconds"] // 60 * 2
```

### New Achievement

Tambah entry di `ACHIEVEMENTS` list di `config/settings.py`:

```python
{"key": "my_ach", "name": "Nama Achievement", "desc": "Deskripsi",
 "icon": "🏆", "xp": 150, "category": "special"},
```

Kemudian tambah checking logic di `core/services/gamification_service.py` `check_achievements()`.

### New Plant Type

Tambah entry di `PLANT_TYPES` dict di `config/settings.py`:

```python
"sunflower": {
    "name": "Bunga Matahari",
    "icon": "🌻",
    "stages": ["🌰", "🌱", "🌿", "🌻", "🌻"],
    "xp_per_stage": [25, 50, 100, 200]
},
```

Kemudian tambah drawing function di `ui/widgets/garden_canvas.py` dan dispatch di `_draw_single_plant()`.

### New Blocking Category

Tambah entry di `BLOCK_CATEGORIES` dict di `config/settings.py`:

```python
"sports": {
    "label": "Olahraga",
    "domains": ["espn.com", "bola.net", "goal.com"],
},
```

Otomatis muncul di Settings page (kategori blokir menggunakan `BLOCK_CATEGORIES` langsung).

---

## Database Changes

### Adding a Column

1. Tambah kolom di schema `core/database.py`
2. Increment `SCHEMA_VERSION`
3. Tambah migration query

```python
# core/database.py
SCHEMA_VERSION = 2

def init_db():
    # ... existing tables ...
    with _conn() as con:
        version = con.execute("PRAGMA user_version").fetchone()[0]
        if version < 2:
            con.execute("ALTER TABLE sessions ADD COLUMN new_col TEXT DEFAULT ''")
            con.execute("PRAGMA user_version = 2")
```

### Adding a Table

1. Tambah `CREATE TABLE IF NOT EXISTS` di `init_db()`
2. Tambah repository functions di file repo yang relevan

---

## Sleep Detection Development

### dlib Dependency

Sleep detection menggunakan dlib (`pip install dlib>=19.24`). Ini adalah **dependency opsional** — aplikasi tetap berjalan tanpa dlib.

**Cek ketersediaan di kode:**
```python
try:
    import dlib
    HAS_DLIB = True
except ImportError:
    HAS_DLIB = False
```

### Model: shape_predictor_68_face_landmarks.dat

Model dilatih oleh Davis King (author dlib) pada dataset iBUG 300-W. Ukuran ~100 MB.

Download otomatis via `_ensure_landmarks_model()` di `face/face_monitor.py`:
1. Cek `~/.antidistract/models/shape_predictor_68_face_landmarks.dat`
2. Jika tidak ada, download dari dlib official URL
3. Di PyInstaller bundle, cek `sys._MEIPASS` dulu

### Eye Aspect Ratio (EAR)

Algoritma dari paper "Real-Time Eye Blink Detection using Facial Landmarks" (Soukupová & Čech, 2016):

```
EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
```

Dimana p1-p6 adalah 6 landmark points per mata (mata kiri: points 36-41, mata kanan: points 42-47).

- EAR ≈ 0.3: mata terbuka normal
- EAR ≈ 0.2: threshold mata tertutup
- EAR ≈ 0.1: mata tertutup rapat

**Implementasi di `face_monitor.py`:**
```python
def _ear(landmarks, eye_points):
    """Hitung Eye Aspect Ratio dari 6 titik landmark."""
    # eye_points: indeks 6 titik dalam 68-landmark array
    pts = [landmarks.part(i) for i in eye_points]
    a = _dist(pts[1], pts[5])  # vertikal atas
    b = _dist(pts[2], pts[4])  # vertikal bawah
    c = _dist(pts[0], pts[3])  # horizontal
    return (a + b) / (2.0 * c)
```

### Testing Sleep Detection

1. Jalankan aplikasi dengan kamera menyala
2. Mulai sesi fokus
3. Tutup mata selama > threshold (default 10 detik)
4. Verifikasi alarm berbunyi (continuous, tidak auto-stop)
5. Buka mata — verifikasi alarm berhenti
6. Cek sleep_detected dan sleep_ended ter-log di console

---

## Testing

### Manual Testing Checklist

Sebelum commit, verifikasi:

- [ ] Aplikasi start tanpa error
- [ ] Database terinisialisasi (`~/.antidistract/antidistract.db` ada)
- [ ] Model face detection terdownload (`~/.antidistract/models/`)
- [ ] Timer Pomodoro bisa start/pause/resume/stop
- [ ] Face detection mendeteksi wajah
- [ ] Sleep detection (jika dlib terinstall): alarm bunyi saat mata tertutup > threshold
- [ ] Persistent alarm: alarm terus bunyi sampai wajah kembali/mata terbuka
- [ ] WebSocket server berjalan (port 8765)
- [ ] Extension terhubung, popup menampilkan stats dan goal bar
- [ ] Blocking bekerja (coba buka youtube.com saat sesi fokus)
- [ ] Keyboard shortcuts: Ctrl+Shift+F/P/B berfungsi
- [ ] Context menu: klik kanan "Blokir situs ini" berfungsi
- [ ] Garden menampilkan tanaman dengan tema light/dark
- [ ] Motivation: daily quote muncul di dashboard
- [ ] Achievements ter-unlock sesuai trigger
- [ ] Data export: CSV sessions dan habits berhasil diexport
- [ ] Settings tersimpan dan persisten antar restart
- [ ] Auto-start break/work berfungsi sesuai setting
- [ ] Tema dark/light berganti tanpa error
- [ ] System tray berfungsi (minimize, restore, quick focus)
- [ ] Build .exe: `python build.py --onefile` sukses, .exe bisa dijalankan

### Quick Import Test

```bash
# Test import semua modul
python -c "
from core.database import init_db; init_db()
from core.repositories.session_repo import *
from core.services.focus_service import FocusService
from core.services.block_service import is_blocked, is_schedule_active
from core.services.gamification_service import on_session_complete
from core.services.garden_service import create_new_plant, get_garden_status
from core.services.motivation_service import get_daily_quote, check_milestones
from core.services.export_service import export_all
from face import FaceMonitor, HAS_DLIB
from network.ws_server import WSServer
print('All imports OK')
print(f'dlib available: {HAS_DLIB}')
"
```

### Cross-Version Smoke Test

```bash
# Test di semua versi Python yang didukung
for ver in 3.9 3.10 3.11 3.12 3.13 3.14; do
    python$ver -c "from face import FaceMonitor; print(f'Python $ver: OK')" || echo "Python $ver: FAILED"
done
```

---

## Building Executable (Windows)

Gunakan script `build.py`:

```bash
pip install pyinstaller

# Single-file executable
python build.py --onefile

# Folder distribusi (startup lebih cepat)
python build.py --onedir

# Bersihkan build cache dulu
python build.py --clean
```

Output: `dist/AntiDistract.exe` (--onefile) atau `dist/AntiDistract/` (--onedir).

**Yang dilakukan build.py:**
- Auto-detect model files dari `~/.antidistract/models/`
- Bundle `deploy.prototxt`, `caffemodel`, dan `shape_predictor_68_face_landmarks.dat` sebagai data files
- Hidden imports: PyQt6, cv2, pyqtgraph, websockets
- Auto-detect icon dari `assets/icons/logo.svg`
- Di runtime, FaceMonitor cek `sys._MEIPASS` dulu untuk path model (PyInstaller bundle), lalu fallback ke `~/.antidistract/models/`

**Catatan penting:**
- Model face detection dan sleep detection HARUS di-bundle. Tanpa itu, fitur deteksi tidak berfungsi di mesin tanpa internet.
- `--hidden-import websockets` diperlukan karena dynamic import oleh asyncio.
- Gunakan `--onedir` untuk development (startup lebih cepat, mudah debug file).

---

## Contributing

1. Fork repository
2. Buat branch fitur: `git checkout -b feat/my-feature`
3. Commit perubahan: `git commit -m "feat: add my feature"`
4. Push ke fork: `git push origin feat/my-feature`
5. Buka Pull Request ke branch `main`

### Commit Conventions

Mengikuti [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — Fitur baru
- `fix:` — Bug fix
- `refactor:` — Perubahan kode tanpa ubah behavior
- `docs:` — Dokumentasi
- `style:` — Formatting, whitespace
- `chore:` — Maintenance task

### PR Guidelines

- Satu PR = satu fitur/fix
- PR description: apa, kenapa, bagaimana
- Screenshot untuk perubahan UI
- Pastikan aplikasi start tanpa error
- **Test di minimal 2 versi Python berbeda** (rekomendasi: 3.9 dan 3.14)
- Jangan commit file model (`*.caffemodel`, `*.prototxt`) — sudah di `.gitignore`
- Jangan commit file di `~/.antidistract/`

---

## Troubleshooting Development

### "Module not found" saat import

```bash
# Pastikan venv aktif
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows

# Reinstall dependencies
pip install -r requirements.txt

# Jika menggunakan editable install:
pip install -e .
```

### Database locked

```bash
# Hapus WAL files (tidak akan kehilangan data)
rm ~/.antidistract/antidistract.db-wal
rm ~/.antidistract/antidistract.db-shm
```

### WebSocket port in use

```bash
# Cari proses yang menggunakan port 8765
netstat -ano | findstr :8765    # Windows
lsof -i :8765                    # Linux/macOS

# Kill proses atau ubah WS_PORT di config/settings.py
```

### Kamera tidak berfungsi di WSL

WSL tidak mendukung akses webcam secara native. Gunakan Windows native Python untuk development dengan face detection. Alternatif: jalankan dengan face detection dinonaktifkan:

```python
# Di main_window.py, tambahkan sebelum face_monitor.start():
self.face_monitor.enabled = False
```

### Model face detection tidak ditemukan

```bash
# Cek apakah model sudah terdownload
ls -la ~/.antidistract/models/

# Jika belum, download manual
mkdir -p ~/.antidistract/models
curl -o ~/.antidistract/models/deploy.prototxt \
  https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt
curl -o ~/.antidistract/models/res10_300x300_ssd_iter_140000.caffemodel \
  https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel
```

---

[Kembali ke README](../README.md)
