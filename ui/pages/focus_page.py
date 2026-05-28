from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox,
    QComboBox, QTextEdit, QButtonGroup, QSizePolicy,
)
from PyQt6.QtCore import Qt

from core.services.focus_service import FocusService, State, Phase
from ui.widgets.glass_card import GlassCard, make_label
from ui.widgets.timer_display import CircularTimer
import config.theme as theme


MOODS = ["", "😫 1", "😐 2", "😊 3", "🤩 4", "🔥 5"]
CATEGORIES = ["umum", "belajar", "coding", "menulis", "membaca", "desain", "riset", "lainnya"]


class FocusPage(QWidget):
    def __init__(self, focus: FocusService, parent=None):
        super().__init__(parent)
        self.focus = focus
        self._toast_timer = None
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 28, 28, 28)
        lay.setSpacing(20)

        # Title
        title = make_label("Fokus Mode", 22, bold=True)
        lay.addWidget(title)

        # Timer card
        timer_card = GlassCard(padding=24)
        timer_lay = QVBoxLayout()
        timer_lay.setContentsMargins(0, 0, 0, 0)
        timer_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._timer = CircularTimer()
        timer_lay.addWidget(self._timer, alignment=Qt.AlignmentFlag.AlignCenter)

        # Controls
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._btn_start = QPushButton("Mulai Fokus")
        self._btn_start.setFixedSize(150, 44)
        self._btn_start.clicked.connect(self._toggle_focus)
        self._btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(self._btn_start)

        self._btn_pause = QPushButton("Pause")
        self._btn_pause.setObjectName("secondary")
        self._btn_pause.setFixedSize(100, 44)
        self._btn_pause.clicked.connect(self._toggle_pause)
        self._btn_pause.setEnabled(False)
        self._btn_pause.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(self._btn_pause)

        self._btn_skip = QPushButton("Skip Fase")
        self._btn_skip.setObjectName("ghost")
        self._btn_skip.setFixedSize(100, 44)
        self._btn_skip.clicked.connect(self._on_skip)
        self._btn_skip.setEnabled(False)
        self._btn_skip.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(self._btn_skip)

        timer_lay.addLayout(btn_row)
        timer_card.addLayout(timer_lay)
        lay.addWidget(timer_card)

        # Bottom row: config + status
        bottom = QHBoxLayout()
        bottom.setSpacing(14)

        # Config card
        config_card = GlassCard()
        config_card.addWidget(make_label("Konfigurasi", 12, color=theme.CURRENT.text_secondary))
        cat_row = QHBoxLayout()
        cat_row.addWidget(make_label("Kategori:", 12))
        self._category_combo = QComboBox()
        self._category_combo.addItems(CATEGORIES)
        self._category_combo.setFixedWidth(140)
        cat_row.addWidget(self._category_combo)
        cat_row.addStretch()
        config_card.addLayout(cat_row)

        self._deep_focus_chk = QCheckBox("Deep Focus (tidak bisa pause)")
        config_card.addWidget(self._deep_focus_chk)

        # Mood
        mood_row = QHBoxLayout()
        mood_row.addWidget(make_label("Mood:", 12))
        self._mood_before = QComboBox()
        self._mood_before.addItems(MOODS)
        self._mood_before.setFixedWidth(100)
        mood_row.addWidget(self._mood_before)
        mood_row.addStretch()
        config_card.addLayout(mood_row)

        # Note
        self._note_input = QTextEdit()
        self._note_input.setPlaceholderText("Catatan sesi...")
        self._note_input.setFixedHeight(60)
        config_card.addWidget(self._note_input)

        bottom.addWidget(config_card)

        # Status card
        status_card = GlassCard()
        status_card.addWidget(make_label("Status", 12, color=theme.CURRENT.text_secondary))

        self._face_label = make_label("Kamera: menunggu...", 12, color=theme.CURRENT.text_secondary)
        status_card.addWidget(self._face_label)

        self._ext_label = make_label("Extension: —", 12, color=theme.CURRENT.text_secondary)
        status_card.addWidget(self._ext_label)

        self._block_label = make_label("Blokir: Nonaktif", 12, color=theme.CURRENT.text_secondary)
        status_card.addWidget(self._block_label)

        status_card.addWidget(QWidget())  # spacer
        bottom.addWidget(status_card)

        lay.addLayout(bottom)

        # Toast notification
        self._toast = make_label("", 12, color=theme.CURRENT.warning)
        self._toast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._toast.setStyleSheet(f"background: {theme.CURRENT.bg_secondary}; border: 1px solid {theme.CURRENT.warning}; border-radius: 8px; padding: 8px 16px;")
        self._toast.hide()
        lay.addWidget(self._toast)

        lay.addStretch()

    def _toggle_focus(self):
        if self.focus.is_active:
            self._stop()
        else:
            self._start()

    def _start(self):
        w = self.window()
        if hasattr(w, 'start_focus'):
            cat = self._category_combo.currentText()
            deep = self._deep_focus_chk.isChecked()
            mood_idx = self._mood_before.currentIndex()
            if mood_idx > 0:
                self.focus.mood_before = mood_idx

            self.focus.note = self._note_input.toPlainText()
            w.start_focus(category=cat, deep_focus=deep)

    def _stop(self):
        w = self.window()
        if hasattr(w, 'stop_focus'):
            w.stop_focus()

    def _toggle_pause(self):
        w = self.window()
        if self.focus.state == State.RUNNING and hasattr(w, 'pause_focus'):
            w.pause_focus()
            self._btn_pause.setText("Lanjutkan")
        elif self.focus.state == State.PAUSED and hasattr(w, 'resume_focus'):
            w.resume_focus()
            self._btn_pause.setText("Pause")

    def _on_skip(self):
        w = self.window()
        if hasattr(w, 'skip_phase'):
            w.skip_phase()

    def on_focus_started(self):
        self._btn_start.setText("Stop Fokus")
        self._btn_start.setObjectName("danger")
        self._btn_start.setStyle(self._btn_start.style())
        self._btn_pause.setEnabled(not self.focus.deep_focus)
        self._btn_pause.setText("Pause")
        self._btn_skip.setEnabled(True)
        self._block_label.setText("Blokir: Aktif")
        self._block_label.setStyleSheet(f"color: {theme.CURRENT.success}; background: transparent; border: none;")

    def on_focus_stopped(self):
        self._btn_start.setText("Mulai Fokus")
        self._btn_start.setObjectName("")
        self._btn_start.setStyle(self._btn_start.style())
        self._btn_pause.setEnabled(False)
        self._btn_pause.setText("Pause")
        self._btn_skip.setEnabled(False)
        self._block_label.setText("Blokir: Nonaktif")
        self._block_label.setStyleSheet(f"color: {theme.CURRENT.text_secondary}; background: transparent; border: none;")
        self._timer.set_values(0.0, "00:00", "", "", "")

    def update_display(self):
        if not self.focus.is_active:
            return

        remaining = self.focus.remaining
        mins, secs = divmod(remaining, 60)
        time_str = f"{mins:02d}:{secs:02d}"

        phase_len = self.focus.phase_length
        elapsed = self.focus.phase_elapsed
        progress = elapsed / phase_len if phase_len > 0 else 0

        if self.focus.phase == Phase.WORK:
            phase_name = "KERJA"
            bar_color = theme.CURRENT.accent
        elif self.focus.phase == Phase.LONG_BREAK:
            phase_name = "ISTIRAHAT PANJANG"
            bar_color = theme.CURRENT.success
        else:
            phase_name = "ISTIRAHAT"
            bar_color = theme.CURRENT.warning

        cycle_str = f"Siklus {self.focus.cycle}"
        self._timer.set_values(progress, time_str, phase_name, cycle_str, bar_color)

    def set_face_status(self, detected: bool, away_s: float):
        if detected:
            self._face_label.setText("Kamera: Wajah terdeteksi")
            self._face_label.setStyleSheet(f"color: {theme.CURRENT.success}; background: transparent; border: none;")
        else:
            self._face_label.setText(f"Kamera: Tidak ada ({int(away_s)}d)")
            color = theme.CURRENT.warning if away_s < 30 else theme.CURRENT.danger
            self._face_label.setStyleSheet(f"color: {color}; background: transparent; border: none;")

    def show_toast(self, message: str, level: str = "warning"):
        from PyQt6.QtCore import QTimer
        color = theme.CURRENT.warning if level == "warning" else theme.CURRENT.danger if level == "critical" else theme.CURRENT.success
        self._toast.setText(message)
        self._toast.setStyleSheet(f"background: {theme.CURRENT.bg_secondary}; border: 1px solid {color}; border-radius: 8px; padding: 8px 16px; color: {color};")
        self._toast.show()
        if self._toast_timer:
            self._toast_timer.stop()
        self._toast_timer = QTimer(self)
        self._toast_timer.setSingleShot(True)
        self._toast_timer.timeout.connect(self._toast.hide)
        self._toast_timer.start(3000)

    def set_extension_status(self, connected: bool):
        if connected:
            self._ext_label.setText("Extension: Terhubung")
            self._ext_label.setStyleSheet(f"color: {theme.CURRENT.success}; background: transparent; border: none;")
        else:
            self._ext_label.setText("Extension: Terputus")
            self._ext_label.setStyleSheet(f"color: {theme.CURRENT.danger}; background: transparent; border: none;")
