from PyQt6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QLabel, QSizePolicy
from PyQt6.QtCore import pyqtSignal, Qt, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QFont

import config.theme as theme


NAV_ITEMS = [
    ("dashboard",  "Dashboard"),
    ("focus",      "Fokus"),
    ("garden",     "Garden"),
    ("habits",     "Kebiasaan"),
    ("analytics",  "Analitik"),
    ("settings",   "Pengaturan"),
]

NAV_ICONS = {
    "dashboard": "📊",
    "focus":     "🎯",
    "garden":    "🌱",
    "habits":    "✅",
    "analytics": "📈",
    "settings":  "⚙️",
}


class Sidebar(QFrame):
    page_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(88)
        self.setStyleSheet(f"""
            Sidebar {{
                background: {theme.CURRENT.sidebar_bg};
                border-right: 1px solid {theme.CURRENT.border};
            }}
        """)
        self._buttons: dict[str, QPushButton] = {}
        self._active = "dashboard"

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 16, 12, 16)
        lay.setSpacing(8)

        logo = QLabel("AD")
        logo.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(f"color: {theme.CURRENT.accent}; background: transparent; border: none; padding: 8px 0;")
        lay.addWidget(logo)

        lay.addSpacing(8)

        for key, label in NAV_ITEMS:
            btn = QPushButton(f"{NAV_ICONS.get(key, '')}")
            btn.setToolTip(label)
            btn.setFixedSize(64, 56)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFont(QFont("Segoe UI", 18))
            btn.clicked.connect(lambda checked, k=key: self._on_click(k))
            self._style_button(btn, key == "dashboard")
            self._buttons[key] = btn
            lay.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        lay.addStretch()

        self._level_lbl = QLabel("Lv. 1")
        self._level_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._level_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._level_lbl.setStyleSheet(f"color: {theme.CURRENT.accent}; background: transparent; border: none;")
        lay.addWidget(self._level_lbl)

    def _style_button(self, btn: QPushButton, active: bool):
        if active:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {theme.CURRENT.accent};
                    color: white;
                    border: none;
                    border-radius: 14px;
                    font-size: 18px;
                }}
                QPushButton:hover {{ background: {theme.CURRENT.accent_hover}; }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {theme.CURRENT.text_secondary};
                    border: none;
                    border-radius: 14px;
                    font-size: 18px;
                }}
                QPushButton:hover {{
                    background: {theme.CURRENT.border};
                    color: {theme.CURRENT.text};
                }}
            """)

    def _on_click(self, key: str):
        if key == self._active:
            return
        old = self._buttons.get(self._active)
        if old:
            self._style_button(old, False)
        new = self._buttons.get(key)
        if new:
            self._style_button(new, True)
        self._active = key
        self.page_changed.emit(key)

    def set_level(self, level: int):
        self._level_lbl.setText(f"Lv. {level}")

    def navigate_to(self, key: str):
        self._on_click(key)
