# User Guide

Panduan lengkap penggunaan semua fitur AntiDistract.

---

## Daftar Isi

1. [Memulai](#memulai)
2. [Dashboard](#dashboard)
3. [Focus Mode](#focus-mode)
4. [Virtual Garden](#virtual-garden)
5. [Habits & Daily Intentions](#habits--daily-intentions)
6. [Analytics](#analytics)
7. [Settings](#settings)
8. [Browser Extension](#browser-extension)
9. [Face Detection & Distraction Alerts](#face-detection--distraction-alerts)
10. [Sleep Detection](#sleep-detection)
11. [Motivation & Milestones](#motivation--milestones)
12. [Data Export](#data-export)
13. [Keyboard Shortcuts](#keyboard-shortcuts)
14. [Gamification & Achievements](#gamification--achievements)

---

## Memulai

### Tampilan Utama

```
┌──────────┬──────────────────────────────────────┐
│          │                                      │
│  Sidebar │         Content Area                 │
│          │                                      │
│  📊      │   ┌─────────────────────────────┐   │
│  🎯      │   │  Halaman yang sedang aktif   │   │
│  🌱      │   │                              │   │
│  ✅      │   └─────────────────────────────┘   │
│  📈      │                                      │
│  ⚙️      │                                      │
│          │                                      │
└──────────┴──────────────────────────────────────┘
```

**Navigasi sidebar (kiri ke kanan):**
1. **Dashboard** — Ringkasan statistik
2. **Focus** — Timer Pomodoro
3. **Garden** — Virtual garden
4. **Habits** — Habit tracker
5. **Analytics** — Grafik & insight
6. **Settings** — Pengaturan

---

## Dashboard

Halaman pertama yang muncul. Menampilkan ringkasan hari ini:

### Stat Cards (atas)

| Card | Keterangan |
|------|-----------|
| Total Belajar Hari Ini | Menit fokus hari ini vs target harian |
| Pergi dari Layar | Berapa kali terdeteksi menjauh |
| Tab Diblokir | Jumlah tab yang diblokir hari ini |
| Streak | Hari berturut-turut fokus |
| Skor Produktivitas | Nilai 0-100 dengan grade A-E |

### Progress Bar

Menunjukkan persentase pencapaian target harian. Hijau jika sudah 100%.

### Weekly Chart

Bar chart 7 hari terakhir — membandingkan fokus time per hari terhadap target.

### Daily Intention

Di bagian header — menampilkan intensi harian yang sudah di-set.

---

## Focus Mode

### Cara Memulai Sesi Fokus

1. Buka halaman **Focus**
2. Pilih **Kategori** (umum, belajar, coding, menulis, membaca, desain, riset, lainnya)
3. (Opsional) Set **Mood** sebelum sesi (1-5)
4. (Opsional) Centang **Deep Focus** untuk mengunci kontrol
5. (Opsional) Tulis catatan sesi
6. Klik **Mulai Fokus**

### Timer Display

Timer berbentuk lingkaran (circular progress) yang menunjukkan:
- **Waktu tersisa** (MM:SS)
- **Fase saat ini**: KERJA / ISTIRAHAT / ISTIRAHAT PANJANG
- **Siklus**: Siklus ke berapa
- **Progress bar**: Gradien warna sesuai fase

### Kontrol Selama Sesi

| Tombol | Fungsi |
|--------|--------|
| Stop Fokus | Menghentikan sesi (tidak tersedia di Deep Focus) |
| Pause | Menjeda sesi. Klik lagi untuk melanjutkan |
| Skip Fase | Langsung pindah ke fase berikutnya |

### Fase Pomodoro

Satu siklus penuh:
```
WORK (25 mnt) → SHORT BREAK (5 mnt) → WORK (25 mnt) → ...
                                    ↓ (setelah 4 siklus)
                              LONG BREAK (15 mnt) → WORK (25 mnt) → ...
```

Semua durasi bisa dikonfigurasi di halaman Settings.

### Status Panel (sisi kanan)

- **Kamera**: Status face detection — wajah terdeteksi / tidak ada
- **Extension**: Status koneksi extension browser — terhubung / terputus
- **Blokir**: Status pemblokiran — aktif (hijau) / nonaktif
- **Toast**: Notifikasi distraksi akan muncul di bagian bawah

### Setelah Sesi Selesai

1. Sesi dicatat ke database
2. XP dihitung dan ditambahkan
3. Tanaman di garden "disiram"
4. Achievement dicek dan di-unlock jika memenuhi syarat
5. Streak diperbarui

---

## Virtual Garden

Tanaman virtual yang tumbuh setiap kali Anda menyelesaikan sesi fokus.

### Menanam Tanaman Baru

1. Pilih jenis tanaman dari dropdown: Pohon, Bunga, Kaktus, Jamur, atau Tanaman
2. Klik **Tanam Baru**
3. Tanaman muncul di garden dengan stage Biji (0)
4. Selesaikan sesi fokus untuk "menyiram" tanaman → dapat XP

### Tahap Pertumbuhan

| Stage | Nama | Keterangan |
|-------|------|-----------|
| 0 | Biji | Baru ditanam, perlu disiram |
| 1 | Tunas | Mulai tumbuh, tunas kecil muncul |
| 2 | Tumbuh | Semakin besar, mulai berbentuk |
| 3 | Mekar | Hampir dewasa, beberapa sudah berbunga |
| 4 | Dewasa | Full grown, bisa "dipanen" |

Setiap jenis tanaman punya XP curve berbeda (lihat tabel di README).

### Interaksi Garden

- **Klik tanaman**: Melihat detail (jenis, stage, XP progress, jumlah sesi)
- **Animasi otomatis**: Bintang berkelap-kelip, partikel melayang, tanaman bergoyang
- **Empty state**: Jika belum ada tanaman, muncul pesan ajakan untuk mulai fokus

---

## Habits & Daily Intentions

### Daily Intention

Satu tujuan utama per hari. Terletak di halaman Habits:

1. Ketik intensi di kolom input
2. Klik **Simpan Intensi**
3. Intensi muncul di header Dashboard sepanjang hari
4. Centang checkbox jika sudah tercapai

### Habit Tracker

Buat kebiasaan yang ingin dilacak:

1. Klik **Tambah Habit**
2. Isi nama, deskripsi, frekuensi (daily/weekly/weekdays), target count
3. Habit muncul di daftar dengan checkbox
4. Centang setiap kali menyelesaikan habit
5. Progress tersimpan per tanggal

Setiap habit yang dicentang memberi XP (+10 XP).

---

## Analytics

Halaman untuk menganalisis pola produktivitas.

### Stat Ringkasan

- Total jam fokus sepanjang waktu
- Rata-rata harian (7 hari)
- Hari terbaik
- Level & XP saat ini

### Weekly Chart

Bar chart fokus 7 hari terakhir — lihat tren naik/turun.

### Tren 30 Hari

Line chart interaktif dengan pyqtgraph — menunjukkan total menit fokus per hari selama 30 hari terakhir.

### Kategori Fokus

Horizontal bar chart — breakdown sesi berdasarkan kategori (coding vs belajar vs membaca, dll).

### Jam Produktif (Heatmap)

24 bar vertikal (jam 00-23) — intensitas warna menunjukkan seberapa banyak Anda fokus di jam tersebut. Gunakan untuk menemukan "golden hours" Anda.

### Achievements Grid

Grid 8 achievement — yang sudah di-unlock tampil dengan warna, yang masih terkunci tampil dengan ikon gembok.

---

## Settings

Halaman konfigurasi lengkap.

### Pomodoro

- Durasi kerja (1-120 menit)
- Durasi istirahat pendek (1-120 menit)
- Durasi istirahat panjang (1-120 menit)
- Jumlah siklus sebelum istirahat panjang (1-10)
- **Auto-start Break** — Otomatis mulai istirahat setelah kerja selesai
- **Auto-start Work** — Otomatis mulai kerja setelah istirahat selesai

### Deteksi Wajah

- Alert setelah tidak terdeteksi (5-300 detik)
- Toggle on/off face detection
- **Deteksi Kantuk** — Toggle on/off sleep detection (hanya jika dlib terinstall)
- **Threshold Kantuk** — Durasi mata tertutup sebelum alarm (5-120 detik, default 10)

### Daftar Blokir

- Input domain manual (contoh: `reddit.com`)
- Tambah/hapus domain dari blocklist
- Daftar domain yang sedang diblokir

### Kategori Blokir

Checklist 5 kategori: Media Sosial, Hiburan, Game, Berita, Belanja. Centang untuk mengaktifkan, hilangkan centang untuk menonaktifkan.

### Jadwal Blokir

- Toggle on/off jadwal otomatis
- Waktu mulai (dari jam)
- Waktu selesai (sampai jam)
- Hari aktif (Senin-Minggu, checklist)

Contoh: Blokir otomatis Senin-Jumat jam 08:00-17:00 (jam kerja).

### Alarm Suara

- Volume master (slider 0-100%)
- Mute checkbox
- Level eskalasi:
  - Level 1: Soft warning — notifikasi ringan
  - Level 2: Warning overlay — suara alert
  - Level 3: Emergency — alarm maksimal + fullscreen

### Pengingat Istirahat

- **Istirahat Mata** (20-20-20 rule): Setiap 20 menit
- **Peregangan**: Setiap 45 menit
- **Hidrasi**: Setiap 90 menit

Masing-masing bisa di-toggle dan intervalnya diatur.

### Target Harian

Target menit fokus per hari (10-720 menit).

### Tema

Dropdown Dark / Light. Perubahan langsung diterapkan.

---

## Browser Extension

### Popup (Klik Icon Extension)

Popup menampilkan:
- **Connection status**: Pulsing dot hijau/merah
- **Focus state**: Timer real-time yang tersisa
- **Phase**: Kerja/Istirahat
- **Stats hari ini**: Menit fokus, tab diblokir, persentase target
- **Goal progress bar**: Visual progress target harian
- **Quick pause**: Jeda 5, 15, atau 30 menit
- **Blocked domains**: Daftar domain/kategori yang diblokir

### Blocked Page

Saat mencoba mengakses domain yang diblokir:

1. Halaman diblokir muncul dengan latar belakang gradient animasi
2. Ikon animasi melayang
3. Kutipan motivasi berganti setiap 8 detik
4. Countdown timer jika blokir berbasis jadwal
5. Tombol "Kembali Bekerja" — menutup tab

### Izin Ekstensi

Extension meminta izin:
- `tabs` — Untuk mendeteksi dan menutup tab
- `webNavigation` — Intersep navigasi sebelum halaman dimuat
- `storage` — Menyimpan state blocking
- `notifications` — Notifikasi desktop
- `alarms` — Timer untuk schedule blocking

---

## Face Detection & Distraction Alerts

### Cara Kerja

1. Kamera menyala saat sesi fokus dimulai
2. OpenCV DNN Face Detection memproses frame setiap ~300ms (3 FPS)
3. Jika wajah tidak terdeteksi, timer away mulai berjalan
4. Alert naik level seiring waktu:

| Waktu Away | Level | Respon |
|------------|-------|--------|
| 15 detik | Level 1 (50% threshold) | Toast notifikasi kuning |
| 30 detik | Level 2 (100% threshold) | Warning overlay + suara alert |
| 45 detik | Level 3 (150% threshold) | Critical fullscreen + alarm darurat + countdown 10 detik |

### Warning Overlay

Overlay fullscreen dengan:
- Judul dan pesan peringatan
- Ikon besar
- Countdown timer (untuk level critical)
- Tombol dismiss (setelah countdown selesai)
- Background blur + animasi pulse (level critical)

---

## Sleep Detection

Mendeteksi kantuk/mengantuk menggunakan Eye Aspect Ratio (EAR) via dlib. **Fitur opsional** — hanya aktif jika dlib terinstall.

### Cara Kerja

1. Kamera mendeteksi 68 titik wajah (facial landmarks)
2. 12 titik di sekitar mata (6 per mata) digunakan untuk menghitung EAR
3. EAR < 0.2 berarti mata tertutup
4. Jika mata tertutup terus-menerus > threshold (default 10 detik), alarm berbunyi
5. Alarm **tidak akan berhenti** sampai mata terbuka kembali

### Konfigurasi

Di halaman **Settings → Deteksi Wajah**:
- **Aktifkan Deteksi Kantuk** — Toggle on/off (hanya muncul jika dlib terinstall)
- **Threshold Kantuk** — Durasi mata tertutup sebelum alarm (5-120 detik, default 10)

### Instalasi dlib

```bash
pip install dlib>=19.24
```

Model `shape_predictor_68_face_landmarks.dat` (~100 MB) akan diunduh otomatis ke `~/.antidistract/models/` saat pertama kali sleep detection dijalankan.

---

## Motivation & Milestones

### Daily Quote

Setiap hari, kutipan motivasi berbeda ditampilkan di Dashboard. Kutipan dalam Bahasa Indonesia dari berbagai tokoh.

### Session Start Quote

Saat memulai sesi fokus, kutipan penyemangat muncul di halaman Focus.

### Milestone Celebrations

Notifikasi khusus muncul saat Anda mencapai:
- **Streak**: 3, 7, 14, 30, 60, 100, 365 hari berturut-turut
- **Level Up**: Setiap 5 level (5, 10, 15, 20, ...)
- **Total Jam**: 100, 500, 1000 jam fokus
- **Tab Diblokir**: 1000, 5000 tab

### Gentle Encouragement

Pesan penyemangat kontekstual saat:
- Kembali ke layar setelah away (face returned)
- Menyelesaikan sesi fokus
- Mencentang habit
- Tab berhasil diblokir

### Weekly Reflection

Ringkasan mingguan di Dashboard dengan positive framing — menunjukkan progres, bukan kekurangan.

---

## Data Export

Export data ke CSV untuk analisis lebih lanjut.

### Cara Export

1. Buka halaman **Analytics**
2. Klik tombol **Export Data** di header
3. Pilih lokasi penyimpanan file

### Format CSV

**Sessions CSV**: date, start_time, end_time, duration_s, category, phase, mood_before, mood_after, distractions, xp_earned

**Habits CSV**: name, frequency, completion_dates, total_completions, active

---

## Keyboard Shortcuts

Shortcut keyboard untuk kontrol cepat tanpa membuka aplikasi:

| Shortcut | Fungsi |
|----------|--------|
| `Ctrl+Shift+F` | Mulai sesi fokus 25 menit |
| `Ctrl+Shift+P` | Pause/Resume sesi |
| `Ctrl+Shift+B` | Toggle blocking on/off |

Shortcut bekerja secara global via browser extension (Chrome/Edge). Pastikan extension terinstall dan terhubung.

### Right-Click Context Menu

Klik kanan di halaman manapun:
- **Blokir situs ini** — Tambah domain ke blocklist
- **Jeda blokir 5 menit** — Pause blocking sementara
- **Buka AntiDistract App** — Fokus ke jendela aplikasi

---

## Gamification & Achievements

### XP System

| Aktivitas | XP |
|-----------|-----|
| Sesi fokus selesai | 50 XP base + 10% per streak day |
| Tab diblokir | 2 XP per block |
| Habit dicentang | 10 XP per habit |
| Intensi harian selesai | 30 XP |
| Mood dicatat | 5 XP |

### Level Progression

Level 1-50+ dengan kurva: `100 × 1.5^(level-1)` XP per level.

### 12 Achievements

| Achievement | Cara Mendapatkan | XP Reward |
|-------------|-----------------|-----------|
| Langkah Pertama | Selesaikan sesi fokus pertama | 50 XP |
| Konsisten! | 3 hari streak | 100 XP |
| Tak Terhentikan | 7 hari streak | 250 XP |
| Legenda Fokus | 30 hari streak | 1000 XP |
| Pomodoro Master | 10 siklus dalam sehari | 150 XP |
| Dedikasi | Total 10 jam fokus | 200 XP |
| Komitmen | Total 100 jam fokus | 1000 XP |
| Jempol Hijau | 5 tanaman di garden | 200 XP |
| Penjaga Fokus | Blokir 100 tab | 150 XP |
| Reflektif | Catat mood 10 kali | 100 XP |
| Early Bird | Sesi sebelum jam 6 pagi | 300 XP |
| Night Owl | Sesi setelah jam 11 malam | 300 XP |

### Productivity Score

Skor harian 0-100 yang dihitung dari:
- Pencapaian target fokus (bobot 40%)
- Rasio distraksi (bobot 25%)
- Penyelesaian habit (bobot 15%)
- Intensi harian (bobot 10%)
- Mood tracking (bobot 10%)

Grade: A (90+), B (80-89), C (70-79), D (60-69), E (<60)

---

[Kembali ke README](../README.md)
