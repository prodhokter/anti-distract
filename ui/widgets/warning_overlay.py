from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, pyqtProperty, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush

import config.theme as theme


class WarningOverlay(QWidget):
    dismissed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.hide()

        self._opacity = 0.0
        self._level = "warning"
        self._message = ""
        self._countdown = 0
        self._pulse = 0.0

        self._anim = QPropertyAnimation(self, b"overlay_opacity")
        self._anim.setDuration(300)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._pulse_timer = QTimer(self)
        self._pulse_timer.setInterval(50)
        self._pulse_timer.timeout.connect(self._pulse_tick)

        self._countdown_timer = QTimer(self)
        self._countdown_timer.setInterval(1000)
        self._countdown_timer.timeout.connect(self._countdown_tick)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._icon_label = QLabel()
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.setFont(QFont("Segoe UI", 72))

        self._title_label = QLabel()
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self._title_label.setStyleSheet(f"color: {theme.CURRENT.text}; background: transparent; border: none;")

        self._msg_label = QLabel()
        self._msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._msg_label.setFont(QFont("Segoe UI", 14))
        self._msg_label.setWordWrap(True)
        self._msg_label.setStyleSheet(f"color: {theme.CURRENT.text_secondary}; background: transparent; border: none;")

        self._countdown_label = QLabel()
        self._countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._countdown_label.setFont(QFont("Segoe UI", 36, QFont.Weight.Light))

        self._btn_dismiss = QPushButton("Saya Kembali Fokus")
        self._btn_dismiss.setFixedSize(220, 48)
        self._btn_dismiss.clicked.connect(self._on_dismiss)
        self._btn_dismiss.setCursor(Qt.CursorShape.PointingHandCursor)

        self._btn_container = QWidget()
        btn_lay = QVBoxLayout(self._btn_container)
        btn_lay.setContentsMargins(0, 0, 0, 0)
        btn_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_lay.addWidget(self._btn_dismiss)

        layout.addStretch()
        layout.addWidget(self._icon_label)
        layout.addSpacing(8)
        layout.addWidget(self._title_label)
        layout.addWidget(self._msg_label)
        layout.addSpacing(8)
        layout.addWidget(self._countdown_label)
        layout.addSpacing(12)
        layout.addWidget(self._btn_container)
        layout.addStretch()

    @pyqtProperty(float)
    def overlay_opacity(self):
        return self._opacity

    @overlay_opacity.setter
    def overlay_opacity(self, val):
        self._opacity = val
        self.update()

    def show_warning(self, level: str, title: str, message: str, icon: str = "⚠️",
                     countdown: int = 0, auto_dismiss: bool = False, dismiss_text: str = "Saya Kembali Fokus"):
        self._level = level
        self._icon_label.setText(icon)
        self._title_label.setText(title)
        self._msg_label.setText(message)
        self._countdown = countdown
        self._dismiss_text = dismiss_text
        self._btn_dismiss.setText(dismiss_text)

        # Color based on level (theme-aware)
        if level == "critical":
            bg = QColor(theme.CURRENT.danger)
            bg.setAlpha(210)
            accent = theme.CURRENT.danger
            title_color = theme.CURRENT.danger
        elif level == "warning":
            bg = QColor(theme.CURRENT.warning)
            bg.setAlpha(200)
            accent = theme.CURRENT.warning
            title_color = theme.CURRENT.warning
        else:
            bg = QColor(theme.CURRENT.accent)
            bg.setAlpha(180)
            accent = theme.CURRENT.accent
            title_color = theme.CURRENT.accent

        self._bg_color = bg
        self._accent_color = QColor(accent)

        self._title_label.setStyleSheet(f"color: {title_color}; background: transparent; border: none; font-weight: bold; font-size: 24px;")

        self._btn_dismiss.setVisible(auto_dismiss)
        self._btn_dismiss.setEnabled(True)

        if countdown > 0:
            self._countdown_label.setText(str(countdown))
            self._countdown_timer.start()
        else:
            self._countdown_label.setText("")
            self._countdown_timer.stop()

        self.resize(self.parent().size())
        self._anim.stop()
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()

        if level == "critical":
            self._pulse_timer.start()
        else:
            self._pulse_timer.stop()

        self.show()
        self.raise_()

    def hide_warning(self):
        self._anim.stop()
        self._anim.setStartValue(self._opacity)
        self._anim.setEndValue(0.0)
        self._anim.start()

        self._pulse_timer.stop()
        self._countdown_timer.stop()

        def _finish():
            self.hide()
        QTimer.singleShot(300, _finish)

    def _pulse_tick(self):
        import math, time
        self._pulse = 0.5 + 0.5 * math.sin(time.time() * 8)
        self.update()

    def _countdown_tick(self):
        self._countdown -= 1
        if self._countdown <= 0:
            self._countdown_timer.stop()
            self._btn_dismiss.setEnabled(True)
            self._countdown_label.setText("")
        else:
            self._countdown_label.setText(str(self._countdown))
            self._countdown_label.setStyleSheet(f"color: {theme.CURRENT.danger}; background: transparent; border: none;")

    def _on_dismiss(self):
        self.dismissed.emit()
        self.hide_warning()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        alpha = int(self._opacity * 255)
        bg = QColor(self._bg_color.red(), self._bg_color.green(), self._bg_color.blue(), int(self._bg_color.alpha() * self._opacity))
        p.fillRect(self.rect(), bg)

        # Pulse border for critical
        if self._level == "critical" and self._pulse > 0.5:
            border_color = QColor(theme.CURRENT.danger)
            border_color.setAlpha(int(alpha * (self._pulse - 0.5) * 2))
            pen = QPen(border_color, 6)
            p.setPen(pen)
            p.drawRect(self.rect().adjusted(3, 3, -3, -3))

        p.end()

    def resizeEvent(self, event):
        if self.parent():
            self.resize(self.parent().size())
        super().resizeEvent(event)
