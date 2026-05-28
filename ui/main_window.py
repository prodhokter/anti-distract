from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget,
    QSystemTrayIcon, QMenu, QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QAction

import core.repositories.session_repo as session_repo
import core.repositories.settings_repo as settings_repo
from core.services.focus_service import FocusService, State, Phase
from core.services.block_service import get_all_block_domains
from core.services.gamification_service import on_session_complete
from core.services.garden_service import water_on_session
from core.services.sound_service import SoundAlarm
from core.services.break_service import BreakReminder, ProductivityScorer, BreakType
from core.services.motivation_service import (
    get_daily_quote, get_random_encouragement, check_milestones, get_session_start_quote,
)
from config.settings import XP_INTENTION, XP_MOOD

from face import FaceMonitor
from face.face_monitor import DEFAULT_SLEEP_THRESHOLD_S
from network.ws_server import WSServer

from ui.widgets.sidebar import Sidebar
from ui.widgets.warning_overlay import WarningOverlay
from ui.pages.dashboard_page import DashboardPage
from ui.pages.focus_page import FocusPage
from ui.pages.garden_page import GardenPage
from ui.pages.habits_page import HabitsPage
from ui.pages.analytics_page import AnalyticsPage
from ui.pages.settings_page import SettingsPage

import config.theme as theme
from config.theme import set_theme, build_stylesheet, DARK


class MainWindow(QMainWindow):
    def __init__(self, ws_server: WSServer):
        super().__init__()
        self.ws_server = ws_server
        self.focus = FocusService()

        self.setWindowTitle("AntiDistract")
        self.setMinimumSize(960, 660)
        self.resize(1024, 720)

        # New services
        self.sound_alarm = SoundAlarm()
        self.break_reminder = BreakReminder()
        self.scorer = ProductivityScorer()

        # Distraction state
        self._away_warning_level = 0
        self._away_warning_timer = QTimer(self)
        self._away_warning_timer.setInterval(5000)
        self._away_warning_timer.timeout.connect(self._escalate_away)

        # Face monitor
        away_sec = int(settings_repo.get_setting("away_threshold_s", "30"))
        self.face_monitor = FaceMonitor(away_threshold=away_sec)
        self.face_monitor.status_changed.connect(self._on_face_status)
        self.face_monitor.away_alert.connect(self._on_away_alert)
        self.face_monitor.face_returned.connect(self._on_face_returned)
        self.face_monitor.sleep_detected.connect(self._on_sleep_detected)
        self.face_monitor.sleep_ended.connect(self._on_sleep_ended)

        # Sleep detection settings
        sleep_enabled = settings_repo.get_setting("sleep_detection_enabled", "1") == "1"
        sleep_threshold = int(settings_repo.get_setting("sleep_threshold_s", str(DEFAULT_SLEEP_THRESHOLD_S)))
        self.face_monitor.set_sleep_detection_enabled(sleep_enabled)
        self.face_monitor.set_sleep_threshold(sleep_threshold)

        self.face_monitor.start()

        # WS callbacks
        ws_server.on_blocked_tab = self._on_blocked_tab
        ws_server.on_pause_request = self._on_ws_pause_request
        ws_server.on_start_request = self._on_ws_start_request
        ws_server.on_stop_request = lambda: self.stop_focus() if self.focus.is_active else None
        ws_server.on_add_block_domain = self._on_ws_add_block_domain

        # Tick timer (1s)
        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(1000)
        self._tick_timer.timeout.connect(self._tick)

        # Break check timer (30s)
        self._break_timer = QTimer(self)
        self._break_timer.setInterval(30_000)
        self._break_timer.timeout.connect(self._check_breaks)

        # Refresh timer
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(10_000)
        self._refresh_timer.timeout.connect(self._refresh_all)
        self._refresh_timer.start()

        self._build_ui()

        # Warning overlay (on top of everything)
        self.warning_overlay = WarningOverlay(self.centralWidget())
        self.warning_overlay.dismissed.connect(self.sound_alarm.stop_all)
        self.warning_overlay.hide()

        self._setup_tray()

        # Sound volume from settings
        vol = float(settings_repo.get_setting("alarm_volume", "0.7"))
        self.sound_alarm.set_master_volume(vol)
        muted = settings_repo.get_setting("alarm_muted", "0") == "1"
        self.sound_alarm.set_muted(muted)

    def _build_ui(self):
        self._central = QWidget()
        self._central.setStyleSheet(f"background: {theme.CURRENT.bg};")
        root = QHBoxLayout(self._central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self._on_nav)
        root.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background: {theme.CURRENT.bg};")

        self.dashboard_page = DashboardPage(self.focus)
        self.focus_page = FocusPage(self.focus)
        self.garden_page = GardenPage()
        self.habits_page = HabitsPage()
        self.analytics_page = AnalyticsPage()
        self.settings_page = SettingsPage(self)

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.focus_page)
        self.stack.addWidget(self.garden_page)
        self.stack.addWidget(self.habits_page)
        self.stack.addWidget(self.analytics_page)
        self.stack.addWidget(self.settings_page)

        root.addWidget(self.stack)
        self.setCentralWidget(self._central)

    def _on_nav(self, key: str):
        pages = {
            "dashboard": 0, "focus": 1, "garden": 2,
            "habits": 3, "analytics": 4, "settings": 5,
        }
        idx = pages.get(key, 0)
        self.stack.setCurrentIndex(idx)
        if key == "dashboard":
            self.dashboard_page.refresh()
        elif key == "garden":
            self.garden_page.refresh()
        elif key == "habits":
            self.habits_page.refresh()
        elif key == "analytics":
            self.analytics_page.refresh()

    # ── Sound helpers ──

    def play_alarm(self, profile: str):
        if not self.sound_alarm.is_muted():
            self.sound_alarm.play(profile)

    # ── System Tray ──

    def _setup_tray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        self.tray.setToolTip("AntiDistract")

        menu = QMenu()
        menu.addAction("Tampilkan", self.show)

        quick_menu = QMenu("Fokus Cepat", menu)
        quick_menu.addAction("Fokus 25 menit", lambda: self.start_focus(category="umum"))
        quick_menu.addAction("Fokus 45 menit", lambda: self._quick_focus(45))
        quick_menu.addAction("Fokus 60 menit", lambda: self._quick_focus(60))
        menu.addMenu(quick_menu)
        menu.addSeparator()
        menu.addAction("Keluar", self._quit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda r: self.show() if r == QSystemTrayIcon.ActivationReason.DoubleClick else None)
        self.tray.show()

    def _quick_focus(self, minutes: int):
        settings_repo.set_setting("pomodoro_work_m", minutes)
        self.start_focus(category="umum")

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray.showMessage("AntiDistract", "App berjalan di background.", QSystemTrayIcon.MessageIcon.Information, 2000)

    def _quit(self):
        if self.focus.is_active:
            self.focus.stop()
        self.face_monitor.stop()
        self.ws_server.stop()
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()

    # ── Tick ──

    def _tick(self):
        result = self.focus.tick()
        self.focus_page.update_display()

        if result:
            phase_name = "Kerja" if result["to"] == "work" else ("Istirahat Panjang" if result["to"] == "long_break" else "Istirahat")
            msg = "Waktunya fokus!" if result["to"] == "work" else "Waktunya istirahat!"
            self.tray.showMessage(f"Fase: {phase_name}", msg, QSystemTrayIcon.MessageIcon.Information, 4000)
            self.play_alarm("focus_end" if result["to"] != "work" else "focus_start")

        if self.focus.is_active:
            self.ws_server.send_focus_state(
                True, self.focus.phase.value, self.focus.remaining,
                self.focus.cycle, self.focus.deep_focus,
                settings_repo.get_blocklist(),
                settings_repo.get_blocked_categories(),
            )

    def _check_breaks(self):
        if not self.focus.is_active or self.focus.phase != Phase.WORK:
            return

        due = self.break_reminder.check()
        for cfg in due:
            self.tray.showMessage(
                f"{cfg.emoji} {cfg.label}",
                cfg.message,
                QSystemTrayIcon.MessageIcon.Information, 6000,
            )
            self.play_alarm("break_reminder")

    # ── Focus control ──

    def start_focus(self, category: str = "umum", deep_focus: bool = False):
        work_m = int(settings_repo.get_setting("pomodoro_work_m", "25"))
        short_m = int(settings_repo.get_setting("pomodoro_break_short_m", "5"))
        long_m = int(settings_repo.get_setting("pomodoro_break_long_m", "15"))
        cycles = int(settings_repo.get_setting("pomodoro_cycles_before_long", "4"))

        self.focus.configure(work_m, short_m, long_m, cycles)
        self.focus.start(category=category, deep_focus=deep_focus)
        self._tick_timer.start()
        self._break_timer.start()
        self.break_reminder.on_session_start()
        self._away_warning_level = 0

        blocklist = settings_repo.get_blocklist()
        categories = settings_repo.get_blocked_categories()
        self.ws_server.send_focus_state(True, "work", self.focus.remaining, 0, deep_focus, blocklist, categories)

        self.focus_page.on_focus_started()
        self.dashboard_page.refresh()
        self.play_alarm("focus_start")

        # Show motivational quote
        quote = get_session_start_quote()
        self.tray.showMessage("Mulai Fokus", quote, QSystemTrayIcon.MessageIcon.Information, 3000)

        if deep_focus:
            self.play_alarm("deep_focus_lock")
            self.warning_overlay.show_warning(
                level="info",
                title="Deep Focus Aktif",
                message=f"Kamu tidak bisa pause atau stop selama sesi ini. Durasi: {work_m} menit. Fokus penuh!",
                icon="🔒",
                countdown=3,
                auto_dismiss=True,
                dismiss_text="Saya Siap!",
            )

    def stop_focus(self):
        result = self.focus.stop()
        self._tick_timer.stop()
        self._break_timer.stop()
        self.break_reminder.reset()
        self.ws_server.send_focus_state(False)
        self.sound_alarm.stop_all()
        self.warning_overlay.hide_warning()

        if result["was_active"] and result["duration_s"] > 0:
            from core.repositories.session_repo import end_session
            end_session(
                session_id=result["session_id"],
                duration_s=result["duration_s"],
                completed=True,
                interruptions=self.focus.interruptions,
                mood_before=self.focus.mood_before,
                mood_after=self.focus.mood_after,
                productivity=self.focus.productivity,
                note=self.focus.note,
                distraction_count=self.focus.distraction_count,
                xp_earned=0,
            )

            # Auto-complete intention + award XP
            intention = session_repo.get_today_intention()
            if intention and not intention.get("completed"):
                session_repo.complete_today_intention()
                session_repo.add_xp(XP_INTENTION)

            # Award mood XP if mood was logged
            if self.focus.mood_before or self.focus.mood_after:
                session_repo.add_xp(XP_MOOD)

            earned = on_session_complete(result["duration_s"], self.focus.distraction_count)
            water_on_session(result["duration_s"] // 60)

            if earned.get("leveled_up"):
                lvl = earned.get("level", 1)
                self.sidebar.set_level(lvl)
                self.tray.showMessage("Level Up!", f"Kamu naik ke Level {lvl}!", QSystemTrayIcon.MessageIcon.Information, 4000)

            for ach in earned.get("achievements", []):
                self.tray.showMessage(
                    f"Achievement: {ach['name']}",
                    f"{ach['description']} +{ach['xp_reward']} XP",
                    QSystemTrayIcon.MessageIcon.Information, 4000,
                )

            # Encouragement + milestones
            enc = get_random_encouragement("session_complete")
            self.tray.showMessage("Sesi Selesai", enc, QSystemTrayIcon.MessageIcon.Information, 4000)

            milestones = check_milestones()
            for m in milestones:
                self.tray.showMessage(m["title"], m["message"], QSystemTrayIcon.MessageIcon.Information, 5000)

        self.focus_page.on_focus_stopped()
        self._away_warning_level = 0
        self._away_warning_timer.stop()
        self._refresh_all()

    def pause_focus(self):
        if self.focus.deep_focus:
            return
        self.focus.pause()
        self.ws_server.send_focus_state(
            False, "", 0, 0, False,
            settings_repo.get_blocklist(),
            settings_repo.get_blocked_categories(),
        )
        self._break_timer.stop()

    def resume_focus(self):
        self.focus.resume()
        self.ws_server.send_focus_state(
            True, self.focus.phase.value, self.focus.remaining,
            self.focus.cycle, self.focus.deep_focus,
            settings_repo.get_blocklist(),
            settings_repo.get_blocked_categories(),
        )
        self._break_timer.start()

    def skip_phase(self):
        self.focus.skip_phase()
        self.focus_page.update_display()

    # ── Distraction Escalation System ──

    @pyqtSlot(bool, float, float)
    def _on_face_status(self, detected: bool, away_s: float, confidence: float):
        self.focus_page.set_face_status(detected, away_s)

        if not detected and away_s > 0 and self.focus.is_active:
            threshold = int(settings_repo.get_setting("away_threshold_s", "30"))

            # Level 1: soft warning (50% threshold)
            if away_s >= threshold * 0.5 and self._away_warning_level == 0:
                self._away_warning_level = 1
                self.focus_page.show_toast("Tetap di depan layar ya!", "warning")

            # Level 2: warning overlay (100% threshold)
            elif away_s >= threshold and self._away_warning_level <= 1:
                self._away_warning_level = 2
                self.sound_alarm.play_continuous("away_warning")
                self.warning_overlay.show_warning(
                    level="warning",
                    title="Kamu ke mana?",
                    message=f"Wajah tidak terdeteksi selama {int(away_s)} detik. Kembali ke layar dan lanjutkan fokus!",
                    icon="👀",
                    countdown=0,
                    auto_dismiss=True,
                    dismiss_text="Saya Kembali",
                )

            # Level 3: critical + emergency alarm (150% threshold)
            elif away_s >= threshold * 1.5 and self._away_warning_level <= 2:
                self._away_warning_level = 3
                self.sound_alarm.play_continuous("away_critical")
                self.warning_overlay.show_warning(
                    level="critical",
                    title="PERINGATAN!",
                    message=f"Kamu sudah meninggalkan layar selama {int(away_s)} detik! Kembali sekarang atau sesi akan di-pause otomatis.",
                    icon="🚨",
                    countdown=10,
                    auto_dismiss=True,
                    dismiss_text="SAYA KEMBALI FOKUS!",
                )

        elif detected and self._away_warning_level > 0:
            self._away_warning_level = 0
            self._away_warning_timer.stop()
            self.sound_alarm.stop_all()
            if self.warning_overlay.isVisible() and self.focus.is_active:
                self.warning_overlay.hide_warning()

    @pyqtSlot(float)
    def _on_away_alert(self, away_s: float):
        session_repo.log_away(away_s, self.focus.session_id)
        self.focus.interruptions += 1
        self.play_alarm("away_warning")
        self.tray.showMessage(
            "Pergi dari layar",
            f"Kamu tidak terdeteksi selama {int(away_s)} detik.",
            QSystemTrayIcon.MessageIcon.Warning, 5000,
        )

    @pyqtSlot()
    def _on_face_returned(self):
        msg = get_random_encouragement("face_returned")
        self.tray.showMessage("Kembali", msg, QSystemTrayIcon.MessageIcon.Information, 3000)

    @pyqtSlot(float)
    def _on_sleep_detected(self, duration_s: float):
        if not self.focus.is_active:
            return
        self.sound_alarm.play_continuous("away_critical")
        self.warning_overlay.show_warning(
            level="critical",
            title="MATA TERTUTUP!",
            message=f"Kamu terdeteksi tidur! Mata tertutup selama {int(duration_s)} detik. Bangun dan lanjutkan fokus!",
            icon="😴",
            countdown=5,
            auto_dismiss=True,
            dismiss_text="SAYA BANGUN!",
        )
        self.tray.showMessage(
            "Tidur Terdeteksi",
            f"Mata tertutup selama {int(duration_s)} detik. Bangun!",
            QSystemTrayIcon.MessageIcon.Critical, 8000,
        )

    @pyqtSlot()
    def _on_sleep_ended(self):
        if self.sound_alarm.is_continuous_active("away_critical"):
            self.sound_alarm.stop_all()
        if self.warning_overlay.isVisible():
            self.warning_overlay.hide_warning()
        self.tray.showMessage("Mata Terbuka", "Kamu sudah bangun. Lanjutkan fokus!", QSystemTrayIcon.MessageIcon.Information, 3000)

    def _escalate_away(self):
        if self._away_warning_level < 3 and self.focus.is_active:
            self._away_warning_level += 1

    # ── Blocked Tab ──

    def _on_blocked_tab(self, url: str, hostname: str, category: str):
        session_repo.log_blocked(url, hostname, category, self.focus.session_id)
        self.focus.distraction_count += 1

        self.play_alarm("tab_blocked")

        dist_count = self.focus.distraction_count
        if dist_count >= 10:
            self.warning_overlay.show_warning(
                level="warning",
                title="Terlalu Banyak Distraksi!",
                message=f"Kamu sudah mencoba membuka {dist_count} tab terlarang. Fokus ke pekerjaanmu!",
                icon="🚫",
                countdown=0,
                auto_dismiss=True,
                dismiss_text="Saya Fokus",
            )

        enc = get_random_encouragement("tab_blocked")
        self.tray.showMessage("Tab Diblokir", enc, QSystemTrayIcon.MessageIcon.Warning, 3000)

    def _on_ws_pause_request(self, duration_m: int):
        if self.focus.deep_focus:
            return
        self.pause_focus()
        QTimer.singleShot(duration_m * 60_000, self.resume_focus)

    def _on_ws_start_request(self, category: str, deep_focus: bool = False):
        if self.focus.is_active:
            return
        self.start_focus(category=category, deep_focus=deep_focus)

    def _on_ws_add_block_domain(self, domain: str):
        bl = settings_repo.get_blocklist()
        if domain not in bl:
            bl.append(domain)
            settings_repo.set_blocklist(bl)
            cats = settings_repo.get_blocked_categories()
            self.ws_server.send_blocklist_update(bl, cats)

    # ── Refresh ──

    def _refresh_all(self):
        self.dashboard_page.refresh()
        self.garden_page.refresh()

    # ── Public helpers ──

    def set_app_theme(self, is_dark: bool):
        set_theme(is_dark)
        from PyQt6.QtWidgets import QApplication
        from config.theme import DARK, LIGHT, CURRENT as C2
        theme = DARK if is_dark else LIGHT
        QApplication.instance().setStyleSheet(build_stylesheet(theme))
        self._central.setStyleSheet(f"background: {C2.bg};")
        self.stack.setStyleSheet(f"background: {C2.bg};")
        settings_repo.set_setting("theme", "dark" if is_dark else "light")

    def get_productivity_score(self) -> dict:
        today = session_repo.get_today_stats()
        intention = session_repo.get_today_intention()
        habits = session_repo.get_habits()
        completions = session_repo.get_today_habit_completions()
        goal = int(settings_repo.get_setting("daily_goal_minutes", "120"))

        return self.scorer.calculate_daily_score(
            focus_minutes=today["total_seconds"] // 60,
            goal_minutes=goal,
            distractions=today["blocked_count"] + today["away_count"],
            habits_completed=len(completions),
            habits_total=len(habits),
            intention_completed=intention.get("completed", False) if intention else False,
            mood_logged=self.focus.mood_before is not None or self.focus.mood_after is not None,
        )
