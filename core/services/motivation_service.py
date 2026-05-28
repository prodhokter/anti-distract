"""Motivation & encouragement service — daily quotes, milestones, reflections."""

import datetime
import random

import core.repositories.session_repo as repo
import core.repositories.settings_repo as settings_repo


# ── Daily Quotes (Indonesian) ─────────────────────────────────

QUOTES = [
    ("Fokus adalah kunci. Tanpa fokus, energi menyebar tanpa hasil.", "Bruce Lee"),
    ("Sukses bukan kebetulan. Sukses adalah kerja keras, ketekunan, belajar, dan pengorbanan.", "Pele"),
    ("Jangan biarkan apa yang tidak bisa kamu lakukan menghentikan apa yang bisa kamu lakukan.", "John Wooden"),
    ("Disiplin adalah jembatan antara tujuan dan pencapaian.", "Jim Rohn"),
    ("Produktivitas tidak pernah kebetulan. Selalu hasil dari komitmen pada keunggulan.", "Paul J. Meyer"),
    ("Kamu tidak bisa mengalahkan orang yang tidak pernah menyerah.", "Babe Ruth"),
    ("Waktu adalah mata uang paling berharga. Jangan habiskan untuk hal yang tidak penting.", "Anonim"),
    ("Satu-satunya cara melakukan pekerjaan hebat adalah mencintai apa yang kamu lakukan.", "Steve Jobs"),
    ("Kesuksesan dimulai dari kebiasaan kecil yang dilakukan setiap hari.", "Anonim"),
    ("Jangan menunggu. Waktu tidak akan pernah 'tepat'. Mulai sekarang juga.", "Napoleon Hill"),
    ("Fokus pada proses, bukan hasil. Hasil akan mengikuti dengan sendirinya.", "Anonim"),
    ("Setiap hari adalah kesempatan baru untuk menjadi lebih baik.", "Anonim"),
    ("Kesuksesan adalah jumlah dari upaya kecil yang diulang hari demi hari.", "Robert Collier"),
    ("Jangan berhenti ketika lelah. Berhentilah ketika selesai.", "Anonim"),
    ("Bermimpilah besar, bekerja keras, tetap rendah hati.", "Anonim"),
    ("Kualitas hidupmu ditentukan oleh kualitas kebiasaanmu.", "Aristoteles"),
    ("Jika kamu ingin sukses, batasi distraksi dan fokus pada prioritas.", "Anonim"),
    ("Kemajuan kecil setiap hari akan menghasilkan hasil besar.", "Anonim"),
    ("Waktu yang kamu nikmati untuk membuang waktu, bukanlah waktu yang terbuang.", "Bertrand Russell"),
    ("Jangan bandingkan perjalananmu dengan orang lain. Setiap orang punya timeline sendiri.", "Anonim"),
    ("Konsistensi mengalahkan intensitas. Lakukan setiap hari, walau sedikit.", "Anonim"),
    ("Fokus berarti mengatakan tidak pada ratusan ide bagus lainnya.", "Steve Jobs"),
    ("Jadilah lebih baik dari dirimu kemarin, bukan lebih baik dari orang lain.", "Anonim"),
    ("Tidak ada yang mustahil. Kata itu sendiri mengatakan 'aku mungkin'.", "Audrey Hepburn"),
    ("Kerja keras mengalahkan bakat ketika bakat tidak bekerja keras.", "Tim Notke"),
    ("Kesempatan tidak datang. Kamu yang menciptakannya.", "Chris Grosser"),
    ("Jadikan setiap sesi fokus sebagai langkah menuju impianmu.", "Anonim"),
    ("Kegagalan adalah kesempatan untuk memulai lagi dengan lebih cerdas.", "Henry Ford"),
    ("Satu-satunya batasan adalah yang kamu tetapkan untuk dirimu sendiri.", "Anonim"),
    ("Fokus pada pertumbuhan, bukan kesempurnaan.", "Anonim"),
    ("Kebiasaan baik sama sulitnya untuk dihilangkan seperti kebiasaan buruk.", "Anonim"),
    ("Bangun pagi, fokus, selesaikan. Ulangi.", "Anonim"),
    ("Hidup dimulai di luar zona nyaman.", "Neale Donald Walsch"),
    ("Lebih baik selesai daripada sempurna.", "Sheryl Sandberg"),
    ("Waktu terbaik untuk menanam pohon adalah 20 tahun lalu. Terbaik kedua adalah sekarang.", "Pepatah Cina"),
    ("Kamu adalah apa yang kamu lakukan, bukan apa yang kamu katakan akan lakukan.", "Carl Jung"),
    ("Rahasia untuk maju adalah memulai.", "Mark Twain"),
    ("Makin keras kamu bekerja untuk sesuatu, makin besar perasaanmu saat mencapainya.", "Anonim"),
    ("Jangan takut gagal. Takutlah tidak mencoba.", "Anonim"),
    ("Lakukan dengan benar, atau tidak sama sekali. Setengah-setengah hanya buang waktu.", "Anonim"),
    ("Tidak ada lift menuju sukses. Kamu harus naik tangga.", "Zig Ziglar"),
    ("Fokus adalah seni memprioritaskan apa yang benar-benar penting.", "Anonim"),
    ("Setiap ahli dulunya pemula yang tidak menyerah.", "Anonim"),
    ("Pikiran yang terfokus adalah salah satu kekuatan paling dahsyat di alam semesta.", "Anonim"),
    ("Jangan menunda. Waktu tidak menunggu.", "Benjamin Franklin"),
    ("Produktif bukan tentang sibuk. Produktif tentang hasil.", "Anonim"),
    ("Ambil risiko atau terima kehidupan biasa-biasa saja.", "Jim Rohn"),
    ("Yang membedakan orang sukses dan gagal adalah kebiasaan harian.", "Anonim"),
    ("Mulailah dari sekarang. Gunakan apa yang ada. Lakukan yang kamu bisa.", "Arthur Ashe"),
    ("Kesuksesan bukan final, kegagalan bukan fatal: yang penting keberanian untuk melanjutkan.", "Winston Churchill"),
]

ENCOURAGEMENTS = {
    "session_complete": [
        "Sesi selesai! Satu langkah lebih dekat ke tujuanmu!",
        "Kerja bagus! Kamu produktif hari ini!",
        "Fokus mode: ON. Kamu hebat!",
        "Satu sesi lagi! Tanamanmu makin besar!",
    ],
    "face_returned": [
        "Bagus! Kembali fokus! Lanjutkan pekerjaanmu.",
        "Wajahmu kembali! Ayo lanjutkan sesinya.",
        "Selamat datang kembali! Tetap semangat!",
    ],
    "habit_check": [
        "Kebiasaan dicentang! Konsistensi adalah kunci!",
        "Satu kebiasaan lagi selesai. Kamu luar biasa!",
        "Kebiasaan kecil, hasil besar. Teruskan!",
    ],
    "tab_blocked": [
        "Akses diblokir. Tetap fokus ya!",
        "Jangan terdistraksi. Pekerjaanmu menunggumu.",
        "Fokus! Kamu lebih kuat dari distraksi.",
    ],
    "break_time": [
        "Waktunya istirahat! Regangkan badanmu.",
        "Istirahat sejenak. Minum air, gerakkan badan.",
        "Rehat dulu. Nanti lanjut lagi dengan semangat baru!",
    ],
}

MILESTONES = [
    (3, "3 Hari Streak!", "Kamu sudah fokus 3 hari berturut-turut! Konsistensi mulai terbentuk."),
    (7, "7 Hari Streak!", "Satu minggu penuh fokus! Kebiasaan produktif sudah mulai terbangun."),
    (14, "14 Hari Streak!", "Dua minggu tanpa putus! Kamu luar biasa konsisten."),
    (30, "30 Hari Streak!", "SATU BULAN! Ini bukan lagi kebiasaan, ini gaya hidup."),
    (60, "60 Hari Streak!", "Dua bulan berturut-turut. Kamu mesin produktivitas!"),
    (100, "100 Hari Streak!", "SERATUS HARI! Pencapaian legendaris. Hormat untukmu!"),
    (365, "365 Hari!", "SATU TAHUN penuh! Kamu adalah definisi disiplin sejati."),
]

LEVEL_MILESTONES = [5, 10, 15, 20, 25, 30, 40, 50]

HOUR_MILESTONES = [10, 25, 50, 100, 250, 500, 1000]


# ── Public API ────────────────────────────────────────────────

def get_daily_quote() -> dict:
    """Return a daily quote based on today's date (stable per day)."""
    today = datetime.date.today()
    seed = today.toordinal()
    idx = seed % len(QUOTES)
    quote, author = QUOTES[idx]
    return {"text": quote, "author": author}


def get_random_encouragement(category: str) -> str:
    """Return a random encouragement message for the given category."""
    messages = ENCOURAGEMENTS.get(category, ["Kamu hebat!"])
    return random.choice(messages)


def check_milestones(user: dict | None = None) -> list[dict]:
    """Check for milestone achievements. Returns list of {title, message} dicts."""
    if user is None:
        user = repo.get_user_progress()

    results = []
    streak = user.get("current_streak", 0)

    # Streak milestones (only trigger on the exact streak day)
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    yesterday_sessions = repo.get_week_stats(1)
    had_yesterday_session = any(r["date"] == yesterday and r.get("total_minutes", 0) > 0 for r in yesterday_sessions)

    for days, title, msg in MILESTONES:
        if streak == days and had_yesterday_session:
            results.append({"title": title, "message": msg})

    # Level milestones
    level = user.get("level", 1)
    last_level_checked = int(settings_repo.get_setting("last_level_milestone", "1"))
    if level in LEVEL_MILESTONES and level > last_level_checked:
        settings_repo.set_setting("last_level_milestone", str(level))
        results.append({
            "title": f"Level {level}!",
            "message": f"Kamu sudah mencapai Level {level}! Terus tingkatkan fokusmu!",
        })

    # Hour milestones
    total_hours = user.get("total_minutes", 0) // 60
    last_hour_checked = int(settings_repo.get_setting("last_hour_milestone", "0"))
    for h in HOUR_MILESTONES:
        if total_hours >= h and h > last_hour_checked:
            settings_repo.set_setting("last_hour_milestone", str(h))
            results.append({
                "title": f"{h} Jam Fokus!",
                "message": f"Kamu sudah fokus selama {h} jam total! Dedikasi yang luar biasa!",
            })

    return results


def get_weekly_reflection() -> dict:
    """Generate a weekly reflection summary."""
    week = repo.get_week_stats(7)
    if not week:
        return {"total_minutes": 0, "avg_minutes": 0, "best_day": None, "message": "Belum ada data minggu ini."}

    total = sum(r["total_minutes"] for r in week)
    avg = total / len(week)
    best = max(week, key=lambda r: r["total_minutes"])
    sessions_this_week = sum(r.get("session_count", 0) for r in week)

    if avg >= 120:
        msg = "Minggu yang sangat produktif! Kamu melampaui target harian rata-rata. Pertahankan!"
    elif avg >= 60:
        msg = "Minggu yang baik! Kamu di jalur yang tepat. Coba tingkatkan sedikit lagi minggu depan."
    elif avg >= 30:
        msg = "Ada kemajuan! Tambah durasi fokus minggu depan untuk hasil lebih maksimal."
    else:
        msg = "Minggu yang santai. Tidak apa-apa. Mulai lagi minggu depan dengan semangat baru!"

    return {
        "total_minutes": total,
        "avg_minutes": int(avg),
        "best_day": best["date"] if best else None,
        "best_minutes": best["total_minutes"] if best else 0,
        "sessions": sessions_this_week,
        "message": msg,
    }


def get_session_start_quote() -> str:
    """Get a short motivational quote to display when starting a focus session."""
    short_quotes = ["Waktunya fokus!", "Saatnya produktif!"]
    idxs = random.sample(range(len(QUOTES)), min(5, len(QUOTES)))
    for i in idxs:
        short_quotes.append(f'"{QUOTES[i][0][:60]}..." — {QUOTES[i][1]}')
    return random.choice(short_quotes)
