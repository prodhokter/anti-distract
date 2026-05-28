from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QRectF, QTimer, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QConicalGradient, QPainterPath

import config.theme as theme


class CircularTimer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(260, 260)
        self._progress = 0.0
        self._time_text = "00:00"
        self._phase_text = ""
        self._cycle_text = ""
        self._bar_color = QColor(theme.CURRENT.accent)
        self._anim = QPropertyAnimation(self, b"progress")
        self._anim.setDuration(400)

    @pyqtProperty(float)
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, val):
        self._progress = val
        self.update()

    def set_values(self, progress: float, time_text: str, phase_text: str, cycle_text: str, bar_color: str = ""):
        self._time_text = time_text
        self._phase_text = phase_text
        self._cycle_text = cycle_text
        if bar_color:
            self._bar_color = QColor(bar_color)

        self._anim.stop()
        self._anim.setStartValue(self._progress)
        self._anim.setEndValue(progress)
        self._anim.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        cx, cy = w / 2, h / 2
        radius = min(w, h) / 2 - 20
        track_w = 14

        # Track background
        pen = QPen(QColor(theme.CURRENT.progress_bg), track_w, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))

        # Progress arc
        if self._progress > 0:
            grad = QConicalGradient(cx, cy, -90)
            grad.setColorAt(0, self._bar_color)
            grad.setColorAt(1, self._bar_color.lighter(130))
            pen = QPen(grad, track_w, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            span = int(-360 * self._progress)
            p.drawArc(QRectF(cx - radius, cy - radius, radius * 2, radius * 2), 90 * 16, span * 16)

        # Time text
        p.setPen(QColor(theme.CURRENT.text))
        font = QFont("Segoe UI", 42, QFont.Weight.Light)
        p.setFont(font)
        p.drawText(QRectF(0, cy - 46, w, 52), Qt.AlignmentFlag.AlignHCenter, self._time_text)

        # Phase text
        if self._phase_text:
            p.setPen(QColor(theme.CURRENT.accent))
            font = QFont("Segoe UI", 11, QFont.Weight.Bold)
            p.setFont(font)
            p.drawText(QRectF(0, cy + 14, w, 20), Qt.AlignmentFlag.AlignHCenter, self._phase_text)

        # Cycle
        if self._cycle_text:
            p.setPen(QColor(theme.CURRENT.text_muted))
            font = QFont("Segoe UI", 10)
            p.setFont(font)
            p.drawText(QRectF(0, cy + 38, w, 18), Qt.AlignmentFlag.AlignHCenter, self._cycle_text)

        p.end()
