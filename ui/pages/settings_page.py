from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QGroupBox, QListWidget, QLineEdit, QCheckBox,
    QScrollArea, QSlider, QComboBox, QTimeEdit,
)
from PyQt6.QtCore import Qt, QTime

import core.repositories.settings_repo as settings_repo
from core.services.block_service import get_all_block_domains, BLOCK_CATEGORIES
from core.services.break_service import BreakType, DEFAULT_BREAKS
from ui.widgets.glass_card import GlassCard, make_label
from config.settings import BLOCK_CATEGORIES
import config.theme as theme

try:
    from face.face_monitor import DEFAULT_SLEEP_THRESHOLD_S, HAS_DLIB
except ImportError:
    DEFAULT_SLEEP_THRESHOLD_S = 10
    HAS_DLIB = False


class SettingsPage(QWidget):
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self._mw = main_window
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(28, 28, 28, 28)
        lay.setSpacing(16)

        lay.addWidget(make_label("Pengaturan", 22, bold=True))

        # ── Pomodoro ──
        grp = QGroupBox("Pomodoro")
        grp_lay = QVBoxLayout(grp)
        for key, label, suffix in [
            ("pomodoro_work_m", "Durasi Kerja", "mnt"),
            ("pomodoro_break_short_m", "Istirahat Pendek", "mnt"),
            ("pomodoro_break_long_m", "Istirahat Panjang", "mnt"),
        ]:
            row = QHBoxLayout()
            row.addWidget(make_label(f"{label}:"))
            sp = QSpinBox()
            sp.setRange(1, 120)
            sp.setValue(int(settings_repo.get_setting(key, "25")))
            sp.setSuffix(f"  {suffix}")
            sp.setFixedWidth(120)
            setattr(self, f"_spin_{key}", sp)
            row.addWidget(sp)
            row.addStretch()
            grp_lay.addLayout(row)

        row = QHBoxLayout()
        row.addWidget(make_label("Siklus sebelum istirahat panjang:"))
        self._spin_cycles = QSpinBox()
        self._spin_cycles.setRange(1, 10)
        self._spin_cycles.setValue(int(settings_repo.get_setting("pomodoro_cycles_before_long", "4")))
        self._spin_cycles.setSuffix("  siklus")
        self._spin_cycles.setFixedWidth(120)
        row.addWidget(self._spin_cycles)
        row.addStretch()
        grp_lay.addLayout(row)

        # Auto-start toggles
        auto_row = QHBoxLayout()
        self._chk_auto_break = QCheckBox("Auto-start istirahat setelah kerja selesai")
        self._chk_auto_break.setChecked(
            settings_repo.get_setting("auto_start_break", "1") == "1"
        )
        auto_row.addWidget(self._chk_auto_break)
        self._chk_auto_work = QCheckBox("Auto-start kerja setelah istirahat")
        self._chk_auto_work.setChecked(
            settings_repo.get_setting("auto_start_work", "0") == "1"
        )
        auto_row.addWidget(self._chk_auto_work)
        auto_row.addStretch()
        grp_lay.addLayout(auto_row)

        btn = QPushButton("Simpan Pomodoro")
        btn.setFixedWidth(150)
        btn.clicked.connect(self._save_pomodoro)
        grp_lay.addWidget(btn)
        lay.addWidget(grp)

        # ── Face Detection ──
        grp2 = QGroupBox("Deteksi Wajah")
        grp2_lay = QVBoxLayout(grp2)
        row = QHBoxLayout()
        row.addWidget(make_label("Alert setelah tidak terdeteksi:"))
        self._spin_away = QSpinBox()
        self._spin_away.setRange(5, 300)
        self._spin_away.setValue(int(settings_repo.get_setting("away_threshold_s", "30")))
        self._spin_away.setSuffix("  detik")
        self._spin_away.setFixedWidth(130)
        row.addWidget(self._spin_away)
        row.addStretch()
        grp2_lay.addLayout(row)

        self._chk_face = QCheckBox("Aktifkan face detection")
        self._chk_face.setChecked(True)
        grp2_lay.addWidget(self._chk_face)

        # Sleep detection
        if HAS_DLIB:
            grp2_lay.addWidget(make_label("Deteksi Tidur (dlib)", 11, bold=True, color=theme.CURRENT.text_secondary))
            self._chk_sleep = QCheckBox("Aktifkan deteksi tidur (mata tertutup)")
            self._chk_sleep.setChecked(
                settings_repo.get_setting("sleep_detection_enabled", "1") == "1"
            )
            grp2_lay.addWidget(self._chk_sleep)

            sleep_row = QHBoxLayout()
            sleep_row.addWidget(make_label("Alert setelah mata tertutup:"))
            self._spin_sleep = QSpinBox()
            self._spin_sleep.setRange(5, 120)
            self._spin_sleep.setValue(int(settings_repo.get_setting(
                "sleep_threshold_s", str(DEFAULT_SLEEP_THRESHOLD_S)
            )))
            self._spin_sleep.setSuffix("  detik")
            self._spin_sleep.setFixedWidth(130)
            sleep_row.addWidget(self._spin_sleep)
            sleep_row.addStretch()
            grp2_lay.addLayout(sleep_row)
        else:
            grp2_lay.addWidget(make_label(
                "Deteksi tidur tidak tersedia (dlib belum terinstall). "
                "Install dengan: pip install dlib",
                10, color=theme.CURRENT.text_muted
            ))

        btn2 = QPushButton("Simpan")
        btn2.setFixedWidth(120)
        btn2.clicked.connect(self._save_face)
        grp2_lay.addWidget(btn2)
        lay.addWidget(grp2)

        # ── Blocklist ──
        grp3 = QGroupBox("Daftar Blokir")
        grp3_lay = QVBoxLayout(grp3)
        self._list_block = QListWidget()
        self._list_block.setFixedHeight(120)
        for d in settings_repo.get_blocklist():
            self._list_block.addItem(d)
        grp3_lay.addWidget(self._list_block)

        add_row = QHBoxLayout()
        self._domain_input = QLineEdit()
        self._domain_input.setPlaceholderText("contoh: reddit.com")
        add_row.addWidget(self._domain_input)
        btn_a = QPushButton("Tambah")
        btn_a.setFixedWidth(80)
        btn_a.clicked.connect(self._add_domain)
        add_row.addWidget(btn_a)
        btn_d = QPushButton("Hapus")
        btn_d.setObjectName("danger")
        btn_d.setFixedWidth(70)
        btn_d.clicked.connect(self._remove_domain)
        add_row.addWidget(btn_d)
        grp3_lay.addLayout(add_row)

        btn3 = QPushButton("Simpan Blocklist")
        btn3.setFixedWidth(140)
        btn3.clicked.connect(self._save_blocklist)
        grp3_lay.addWidget(btn3)
        lay.addWidget(grp3)

        # ── Block Categories ──
        grp_cats = QGroupBox("Kategori Blokir")
        cats_lay = QVBoxLayout(grp_cats)
        self._cat_checks = {}
        active = settings_repo.get_blocked_categories()
        for key, data in BLOCK_CATEGORIES.items():
            chk = QCheckBox(data["label"])
            chk.setChecked(key in active)
            self._cat_checks[key] = chk
            cats_lay.addWidget(chk)
        btn_cats = QPushButton("Simpan Kategori")
        btn_cats.setFixedWidth(140)
        btn_cats.clicked.connect(self._save_categories)
        cats_lay.addWidget(btn_cats)
        lay.addWidget(grp_cats)

        # ── Block Schedule ──
        grp_sched = QGroupBox("Jadwal Blokir Otomatis")
        sched_lay = QVBoxLayout(grp_sched)

        self._chk_schedule = QCheckBox("Aktifkan jadwal blokir")
        self._chk_schedule.setChecked(
            settings_repo.get_setting("block_schedule_enabled", "0") == "1"
        )
        sched_lay.addWidget(self._chk_schedule)

        time_row = QHBoxLayout()
        time_row.addWidget(make_label("Dari:"))
        self._time_start = QTimeEdit()
        start_val = settings_repo.get_setting("block_schedule_start", "08:00")
        h, m = map(int, start_val.split(":"))
        self._time_start.setTime(QTime(h, m))
        self._time_start.setFixedWidth(100)
        time_row.addWidget(self._time_start)

        time_row.addWidget(make_label("Sampai:"))
        self._time_end = QTimeEdit()
        end_val = settings_repo.get_setting("block_schedule_end", "17:00")
        h, m = map(int, end_val.split(":"))
        self._time_end.setTime(QTime(h, m))
        self._time_end.setFixedWidth(100)
        time_row.addWidget(self._time_end)
        time_row.addStretch()
        sched_lay.addLayout(time_row)

        days_row = QHBoxLayout()
        days_row.addWidget(make_label("Hari:"))
        day_names = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
        self._day_checks = {}
        active_days = settings_repo.get_setting("block_schedule_days", "1,2,3,4,5")
        active_list = [d.strip() for d in active_days.split(",") if d.strip()]
        for i, name in enumerate(day_names):
            day_num = str((i + 1) % 7) if i < 6 else "0"
            chk = QCheckBox(name)
            chk.setChecked(day_num in active_list)
            self._day_checks[day_num] = chk
            days_row.addWidget(chk)
        days_row.addStretch()
        sched_lay.addLayout(days_row)

        btn_sched = QPushButton("Simpan Jadwal")
        btn_sched.setFixedWidth(130)
        btn_sched.clicked.connect(self._save_schedule)
        sched_lay.addWidget(btn_sched)
        lay.addWidget(grp_sched)

        # ── Sound Alarm ──
        grp_sound = QGroupBox("Alarm Suara")
        sound_lay = QVBoxLayout(grp_sound)

        vol_row = QHBoxLayout()
        vol_row.addWidget(make_label("Volume Master:"))
        self._slider_volume = QSlider(Qt.Orientation.Horizontal)
        self._slider_volume.setRange(0, 100)
        self._slider_volume.setValue(int(float(settings_repo.get_setting("alarm_volume", "0.7")) * 100))
        self._slider_volume.setFixedWidth(180)
        self._slider_volume.valueChanged.connect(self._on_volume_change)
        vol_row.addWidget(self._slider_volume)
        self._vol_label = make_label(f"{self._slider_volume.value()}%", 12, color=theme.CURRENT.accent)
        vol_row.addWidget(self._vol_label)
        vol_row.addStretch()
        sound_lay.addLayout(vol_row)

        self._chk_mute = QCheckBox("Mute semua alarm")
        self._chk_mute.setChecked(settings_repo.get_setting("alarm_muted", "0") == "1")
        self._chk_mute.toggled.connect(self._on_mute_toggle)
        sound_lay.addWidget(self._chk_mute)

        sound_lay.addWidget(make_label("Saat terdistraksi (away/tab blocked), alarm akan berbunyi sesuai level:", 11, color=theme.CURRENT.text_secondary))
        sound_lay.addWidget(make_label("Level 1: Soft warning (50% threshold) — notifikasi ringan", 10, color=theme.CURRENT.text_muted))
        sound_lay.addWidget(make_label("Level 2: Warning overlay (100% threshold) — suara alert", 10, color=theme.CURRENT.text_muted))
        sound_lay.addWidget(make_label("Level 3: Emergency (150% threshold) — alarm maksimal + fullscreen", 10, color=theme.CURRENT.text_muted))

        btn_sound = QPushButton("Simpan Pengaturan Suara")
        btn_sound.setFixedWidth(180)
        btn_sound.clicked.connect(self._save_sound)
        sound_lay.addWidget(btn_sound)
        lay.addWidget(grp_sound)

        # ── Break Reminders ──
        grp_break = QGroupBox("Pengingat Istirahat")
        break_lay = QVBoxLayout(grp_break)
        self._break_configs = {}
        for cfg in DEFAULT_BREAKS:
            row = QHBoxLayout()
            chk = QCheckBox(f"{cfg.emoji} {cfg.label}")
            chk.setChecked(cfg.enabled)
            chk.toggled.connect(lambda on, bt=cfg.break_type: self._on_break_toggle(bt, on))
            row.addWidget(chk)

            sp = QSpinBox()
            sp.setRange(5, 300)
            sp.setValue(cfg.interval_minutes)
            sp.setSuffix(" mnt")
            sp.setFixedWidth(100)
            row.addWidget(sp)

            row.addWidget(make_label(cfg.message[:50] + "...", 10, color=theme.CURRENT.text_muted))
            row.addStretch()
            self._break_configs[cfg.break_type.value] = {"check": chk, "spin": sp}
            break_lay.addLayout(row)

        btn_break = QPushButton("Simpan Pengingat")
        btn_break.setFixedWidth(150)
        btn_break.clicked.connect(self._save_breaks)
        break_lay.addWidget(btn_break)
        lay.addWidget(grp_break)

        # ── Daily Goal ──
        grp_goal = QGroupBox("Target Harian")
        goal_lay = QHBoxLayout(grp_goal)
        goal_lay.addWidget(make_label("Target (menit):"))
        self._spin_goal = QSpinBox()
        self._spin_goal.setRange(10, 720)
        self._spin_goal.setValue(int(settings_repo.get_setting("daily_goal_minutes", "120")))
        self._spin_goal.setSuffix("  mnt")
        self._spin_goal.setFixedWidth(130)
        goal_lay.addWidget(self._spin_goal)
        goal_lay.addStretch()
        btn_g = QPushButton("Simpan")
        btn_g.setFixedWidth(100)
        btn_g.clicked.connect(lambda: settings_repo.set_setting("daily_goal_minutes", self._spin_goal.value()))
        goal_lay.addWidget(btn_g)
        lay.addWidget(grp_goal)

        # ── Theme ──
        grp_theme = QGroupBox("Tema")
        theme_lay = QHBoxLayout(grp_theme)
        theme_lay.addWidget(make_label("Tema:"))
        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["Light", "Dark"])
        current_theme = settings_repo.get_setting("theme", "light")
        self._theme_combo.setCurrentText(current_theme.capitalize())
        self._theme_combo.setFixedWidth(120)
        self._theme_combo.currentTextChanged.connect(self._on_theme_change)
        theme_lay.addWidget(self._theme_combo)
        theme_lay.addStretch()
        lay.addWidget(grp_theme)

        lay.addStretch()
        scroll.setWidget(container)
        outer.addWidget(scroll)

    # ── Save actions ──

    def _save_pomodoro(self):
        for key in ["pomodoro_work_m", "pomodoro_break_short_m", "pomodoro_break_long_m"]:
            sp = getattr(self, f"_spin_{key}", None)
            if sp:
                settings_repo.set_setting(key, sp.value())
        settings_repo.set_setting("pomodoro_cycles_before_long", self._spin_cycles.value())
        settings_repo.set_setting("auto_start_break", "1" if self._chk_auto_break.isChecked() else "0")
        settings_repo.set_setting("auto_start_work", "1" if self._chk_auto_work.isChecked() else "0")

        if self._mw and self._mw.focus.is_active:
            self._mw.focus.configure(
                int(settings_repo.get_setting("pomodoro_work_m", "25")),
                int(settings_repo.get_setting("pomodoro_break_short_m", "5")),
                int(settings_repo.get_setting("pomodoro_break_long_m", "15")),
                int(settings_repo.get_setting("pomodoro_cycles_before_long", "4")),
            )

    def _save_face(self):
        sec = self._spin_away.value()
        settings_repo.set_setting("away_threshold_s", sec)
        if self._mw:
            self._mw.face_monitor.set_threshold(sec)
            self._mw.face_monitor.enabled = self._chk_face.isChecked()

            if HAS_DLIB:
                sleep_enabled = self._chk_sleep.isChecked()
                sleep_sec = self._spin_sleep.value()
                settings_repo.set_setting("sleep_detection_enabled", "1" if sleep_enabled else "0")
                settings_repo.set_setting("sleep_threshold_s", sleep_sec)
                self._mw.face_monitor.set_sleep_detection_enabled(sleep_enabled)
                self._mw.face_monitor.set_sleep_threshold(sleep_sec)

    def _add_domain(self):
        domain = self._domain_input.text().strip().lower()
        if not domain:
            return
        domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
        bl = settings_repo.get_blocklist()
        if domain not in bl:
            bl.append(domain)
            settings_repo.set_blocklist(bl)
            self._list_block.addItem(domain)
        self._domain_input.clear()

    def _remove_domain(self):
        row = self._list_block.currentRow()
        if row < 0:
            return
        domain = self._list_block.item(row).text()
        bl = settings_repo.get_blocklist()
        if domain in bl:
            bl.remove(domain)
            settings_repo.set_blocklist(bl)
        self._list_block.takeItem(row)

    def _save_blocklist(self):
        bl = [self._list_block.item(i).text() for i in range(self._list_block.count())]
        settings_repo.set_blocklist(bl)
        if self._mw:
            cats = settings_repo.get_blocked_categories()
            self._mw.ws_server.send_blocklist_update(bl, cats)

    def _save_categories(self):
        cats = [k for k, chk in self._cat_checks.items() if chk.isChecked()]
        settings_repo.set_blocked_categories(cats)
        if self._mw:
            bl = settings_repo.get_blocklist()
            self._mw.ws_server.send_blocklist_update(bl, cats)

    def _save_schedule(self):
        settings_repo.set_setting(
            "block_schedule_enabled",
            "1" if self._chk_schedule.isChecked() else "0",
        )
        settings_repo.set_setting(
            "block_schedule_start",
            self._time_start.time().toString("HH:mm"),
        )
        settings_repo.set_setting(
            "block_schedule_end",
            self._time_end.time().toString("HH:mm"),
        )
        active_days = [k for k, chk in self._day_checks.items() if chk.isChecked()]
        settings_repo.set_setting("block_schedule_days", ",".join(active_days))
        if self._mw:
            bl = settings_repo.get_blocklist()
            cats = settings_repo.get_blocked_categories()
            self._mw.ws_server.send_blocklist_update(bl, cats)

    def _on_volume_change(self, val):
        self._vol_label.setText(f"{val}%")

    def _on_mute_toggle(self, muted):
        if self._mw:
            self._mw.sound_alarm.set_muted(muted)

    def _on_theme_change(self, theme_name: str):
        if self._mw:
            self._mw.set_app_theme(theme_name.lower() == "dark")

    def _save_sound(self):
        vol = self._slider_volume.value() / 100.0
        settings_repo.set_setting("alarm_volume", vol)
        settings_repo.set_setting("alarm_muted", "1" if self._chk_mute.isChecked() else "0")
        if self._mw:
            self._mw.sound_alarm.set_master_volume(vol)
            self._mw.sound_alarm.set_muted(self._chk_mute.isChecked())

    def _on_break_toggle(self, bt: BreakType, enabled: bool):
        if self._mw:
            self._mw.break_reminder.set_enabled(bt, enabled)

    def _save_breaks(self):
        if self._mw:
            for key, cfg in self._break_configs.items():
                bt = BreakType(key)
                enabled = cfg["check"].isChecked()
                interval = cfg["spin"].value()
                self._mw.break_reminder.set_enabled(bt, enabled)
                self._mw.break_reminder.set_interval(bt, interval)
