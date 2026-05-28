# Installation Guide

Panduan instalasi lengkap untuk aplikasi desktop AntiDistract dan browser extension. Mendukung Windows, macOS, dan Linux.

---

## Prasyarat

| Komponen | Minimal | Rekomendasi |
|----------|---------|-------------|
| Python | 3.9 | 3.12+ |
| pip | 22.0+ | 24.0+ |
| Sistem Operasi | Windows 10 / macOS 12 / Ubuntu 22.04 | Windows 11 / macOS 15 / Ubuntu 24.04 |
| Browser | Chrome 110+ / Edge 110+ | Chrome 130+ |
| Webcam | 720p | 1080p (untuk face detection) |
| RAM | 4 GB | 8 GB |
| Disk | 500 MB | 1 GB (termasuk model ~11 MB) |

---

## Instalasi Aplikasi Desktop

### Langkah 1: Clone Repository

```bash
git clone https://github.com/prodhokter/anti-distract.git
cd anti-distract
```

### Langkah 2: Buat Virtual Environment (Direkomendasikan)

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Langkah 3: Install Dependencies

**Metode A — pip + requirements.txt (Direkomendasikan):**

```bash
pip install -r requirements.txt
```

**Metode B — pip install via pyproject.toml:**

```bash
# Install sebagai package
pip install .

# Atau editable install (untuk development)
pip install -e .
```

Setelah install via metode B, aplikasi bisa dijalankan dengan command `anti-distract` langsung dari terminal.

Daftar dependency yang akan terinstal:

| Package | Versi | Fungsi |
|---------|-------|--------|
| PyQt6 | 6.8+ | GUI framework — native desktop UI |
| opencv-python | 4.10+ | Kamera, image processing & AI face detection (OpenCV DNN) |
| websockets | 14+ | WebSocket server — real-time extension sync |
| pyqtgraph | 0.13+ | Interactive charts & visualisasi data |
| dlib | 19.24+ | (Opsional) Sleep/drowsiness detection via Eye Aspect Ratio |

### Langkah 4: Jalankan Aplikasi

```bash
python main.py
# atau jika install via pyproject.toml:
anti-distract
```

### Langkah 5: Download Model (Otomatis)

Pada first run, model face detection otomatis diunduh ke `~/.antidistract/models/`:

- `deploy.prototxt` (~3 KB) — Caffe model architecture
- `res10_300x300_ssd_iter_140000.caffemodel` (~10.7 MB) — Pre-trained weights

**Sleep detection (opsional):** Jika dlib terinstall, model tambahan akan diunduh:
- `shape_predictor_68_face_landmarks.dat` (~100 MB) — dlib 68-point facial landmarks

Internet hanya diperlukan untuk one-time download ini. Setelah itu, semua deteksi berjalan sepenuhnya offline.

**Jika mesin tidak ada akses internet**, download model manual:

```bash
mkdir -p ~/.antidistract/models

curl -o ~/.antidistract/models/deploy.prototxt \
  https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt

curl -o ~/.antidistract/models/res10_300x300_ssd_iter_140000.caffemodel \
  https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel
```

### Verifikasi Instalasi

1. Aplikasi akan membuka jendela utama (960×660) dengan sidebar navigasi 6 halaman
2. Database otomatis terinisialisasi di `~/.antidistract/antidistract.db`
3. WebSocket server berjalan di `localhost:8765`
4. Kamera akan mulai mendeteksi wajah (indikator status di halaman Fokus)
5. Model file terdownload di `~/.antidistract/models/`

---

## Platform-Specific Notes

### Linux

**Dependency sistem yang diperlukan:**

```bash
# Ubuntu/Debian
sudo apt install libxcb-cursor0 libpulse0

# Fedora
sudo dnf install libxcb pulseaudio-libs

# Arch Linux
sudo pacman -S libxcb pulseaudio
```

Jika menggunakan Linux dan mengalami error `externally-managed-environment` saat pip install:

```bash
pip install --break-system-packages -r requirements.txt
```

### macOS

- OpenCV DNN berjalan native di Apple Silicon (ARM64) dan Intel (x86_64) — tanpa Rosetta
- Izinkan akses kamera di **System Preferences → Privacy & Security → Camera** saat diminta
- Tidak ada dependency sistem tambahan yang diperlukan

### Windows

- Webcam harus tersedia dan tidak digunakan aplikasi lain
- Face detection otomatis menonaktifkan diri jika kamera tidak ditemukan
- Tidak ada dependency sistem tambahan

---

## Instalasi Browser Extension

### Chrome

1. Buka `chrome://extensions`
2. Aktifkan **Developer mode** (toggle di pojok kanan atas)
3. Klik **Load unpacked**
4. Pilih folder `extension/` dari direktori project ini
5. Extension akan muncul dengan ikon AntiDistract di toolbar

### Edge

1. Buka `edge://extensions`
2. Aktifkan **Developer mode** (toggle di kiri bawah)
3. Klik **Load unpacked**
4. Pilih folder `extension/` dari direktori project ini

### Verifikasi Koneksi Extension

1. Jalankan aplikasi desktop (`python main.py`)
2. Klik ikon extension di toolbar browser
3. Popup menampilkan status koneksi:
   - **Green pulsing dot** — Connected, focus state real-time synced
   - **Red dot** — Disconnected (pastikan aplikasi desktop berjalan)

**Jika extension tidak terhubung:**
- Pastikan aplikasi desktop sedang berjalan dan WebSocket server aktif
- Periksa apakah port 8765 tersedia (tidak diblokir firewall)
- Klik kanan extension → "Reload extension"
- Cek console extension: klik kanan icon extension → Inspect → tab Console

---

## Auto-Start Saat Boot

### Windows

```bash
# Install ke startup registry
python scripts/setup_autostart.py install

# Cek status
python scripts/setup_autostart.py status

# Hapus dari startup
python scripts/setup_autostart.py remove
```

Entry ditambahkan di `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`.

### Linux (GNOME/KDE/XFCE)

```bash
mkdir -p ~/.config/autostart

cat > ~/.config/autostart/antidistract.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=AntiDistract
Comment=Advanced Productivity Tracker
Exec=bash -c "cd /path/to/anti-distract && python3 main.py"
Icon=/path/to/anti-distract/assets/icons/icon.png
Terminal=false
StartupNotify=false
X-GNOME-Autostart-enabled=true
EOF
```

Ganti `/path/to/anti-distract` dengan path absolut ke direktori project.

### macOS

```bash
# Buka System Preferences → General → Login Items
# Klik + dan tambahkan script launcher

# Atau via terminal:
osascript -e 'tell application "System Events" to make login item at end with properties {path:"/path/to/anti-distract/main.py", hidden:false}'
```

### Auto-Start Browser (Opsional)

Untuk memastikan extension berjalan, tambahkan browser ke startup:

**Windows**: Shortcut Chrome/Edge di folder:
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\
```

**Linux**:
```bash
cp /usr/share/applications/google-chrome.desktop ~/.config/autostart/
```

---

## Struktur Data

Semua data tersimpan di `~/.antidistract/`:

```
~/.antidistract/
├── antidistract.db          # Database SQLite (semua data user)
├── antidistract.db-wal      # Write-Ahead Log (WAL mode)
├── antidistract.db-shm      # Shared Memory index
├── models/                  # Model face detection (auto-download)
│   ├── deploy.prototxt      # Caffe model architecture (~3 KB)
│   └── res10_300x300_ssd_iter_140000.caffemodel  # Weights (~10.7 MB)
└── sounds/                  # File WAV yang digenerate secara programmatic
    ├── sine_440hz.wav
    ├── dual_tone.wav
    ├── emergency.wav
    ├── buzzer.wav
    └── bell.wav
```

---

## Troubleshooting

### "No module named 'PyQt6'"

```bash
pip install PyQt6>=6.8.0
```

### Kamera tidak terdeteksi

1. Pastikan tidak ada aplikasi lain yang menggunakan kamera (Zoom, Teams, browser)
2. Restart aplikasi
3. Cek device manager (Windows) atau `ls /dev/video*` (Linux)
4. macOS: cek System Preferences → Privacy → Camera — pastikan Terminal/VS Code diizinkan
5. Face detection otomatis nonaktif jika kamera tidak tersedia — fitur lain tetap berfungsi normal

### WebSocket gagal start (port 8765 digunakan)

```bash
# Windows
netstat -ano | findstr :8765

# Linux/macOS
lsof -i :8765
```

Matikan proses yang menggunakan port tersebut, atau ubah `WS_PORT` di `config/settings.py`.

### Extension tidak bisa konek

1. Pastikan aplikasi desktop berjalan (`python main.py`)
2. Reload extension di `chrome://extensions`
3. Cek console extension (klik kanan extension → Inspect → Console)
4. Pastikan tidak ada firewall blocking `localhost:8765`
5. Coba koneksi manual: buka `http://localhost:8765` di browser (harusnya "Upgrade Required" atau error WebSocket)

### Face detection model gagal download

1. Cek koneksi internet
2. Download manual — lihat [Langkah 5](#langkah-5-download-model-otomatis) untuk URL
3. Letakkan file di `~/.antidistract/models/`

### Performa lambat

- Face detection berjalan di ~3 FPS — cukup untuk presence detection, bukan performance issue
- Matikan animasi Garden: naikkan interval timer di `ui/widgets/garden_canvas.py`
- Extension blocking hanya aktif saat sesi fokus berjalan — tidak ada overhead saat idle
- Database SQLite dengan WAL mode — concurrent read/write tanpa lock

### Linux: Qt platform plugin error

```bash
# Install dependency yang diperlukan
sudo apt install libxcb-cursor0 libpulse0

# Fallback ke offscreen rendering (tanpa GUI)
QT_QPA_PLATFORM=offscreen python main.py
```

---

## Uninstall

```bash
# Hapus dari startup (jika terpasang)
python scripts/setup_autostart.py remove

# Hapus semua data aplikasi
rm -rf ~/.antidistract

# Hapus project directory
rm -rf anti-distract

# Hapus virtual environment (jika ada)
rm -rf venv
```

**Browser Extension**: Buka `chrome://extensions` → klik "Remove" pada AntiDistract.

---

## Build Executable (Windows)

Gunakan script `build.py` untuk generate standalone `.exe`:

```bash
pip install pyinstaller

# Single-file executable
python build.py --onefile

# Folder distribusi (startup lebih cepat, mudah debug)
python build.py --onedir

# Bersihkan build cache dulu
python build.py --clean
```

Output di `dist/AntiDistract.exe` (--onefile) atau `dist/AntiDistract/` (--onedir).

Model face detection dan sleep detection otomatis di-bundle ke dalam executable. Tidak perlu internet saat menjalankan `.exe`.

---

[Kembali ke README](../README.md)
