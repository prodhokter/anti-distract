import datetime
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import config.theme as theme


class WeekBarChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)
        self._bars: list[QFrame] = []

    def set_data(self, data: list[dict], goal_minutes: int = 120):
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        today = datetime.date.today()
        stats = {r["date"]: r for r in data}

        for i in range(6, -1, -1):
            d = today - datetime.timedelta(days=i)
            key = d.isoformat()
            entry = stats.get(key, {})
            mins = entry.get("total_minutes", 0)
            pct = min(100, int(mins / goal_minutes * 100)) if goal_minutes else 0

            if pct >= 100:
                color = theme.CURRENT.success
            elif pct > 0:
                color = theme.CURRENT.accent
            else:
                color = theme.CURRENT.border

            col = QVBoxLayout()
            col.setSpacing(5)
            col.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)

            bar = QFrame()
            bar_h = max(4, int(pct * 0.7))
            bar.setFixedSize(34, bar_h)
            bar.setStyleSheet(f"background: {color}; border-radius: 5px;")

            day_lbl = QLabel(d.strftime("%a"))
            day_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            day_lbl.setFont(QFont("Segoe UI", 9))
            day_lbl.setStyleSheet(f"color: {theme.CURRENT.text_muted}; background: transparent; border: none;")

            min_lbl = QLabel(f"{int(mins)}m")
            min_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            min_lbl.setFont(QFont("Segoe UI", 8))
            min_lbl.setStyleSheet(f"color: {theme.CURRENT.text_secondary}; background: transparent; border: none;")

            col.addWidget(bar, alignment=Qt.AlignmentFlag.AlignHCenter)
            col.addWidget(day_lbl)
            col.addWidget(min_lbl)

            wrap = QWidget()
            wrap.setLayout(col)
            self._layout.addWidget(wrap)
