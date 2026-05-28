from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import config.theme as theme


def make_label(text, size=13, bold=False, color=None) -> QLabel:
    lbl = QLabel(text)
    font = QFont("Segoe UI", size)
    font.setBold(bold)
    lbl.setFont(font)
    lbl.setStyleSheet(f"color: {color or theme.CURRENT.text}; background: transparent; border: none;")
    return lbl


class GlassCard(QFrame):
    def __init__(self, parent=None, padding=16):
        super().__init__(parent)
        self.setStyleSheet(f"""
            GlassCard {{
                background: {theme.CURRENT.card_bg};
                border: 1px solid {theme.CURRENT.border};
                border-radius: 12px;
            }}
        """)
        self._padding = padding
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(padding, padding - 2, padding, padding - 2)
        self._layout.setSpacing(8)

    def addWidget(self, w):
        self._layout.addWidget(w)

    def addLayout(self, lay):
        self._layout.addLayout(lay)


class StatCard(QFrame):
    def __init__(self, title: str, value: str = "—", subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            StatCard {{
                background: {theme.CURRENT.card_bg};
                border: 1px solid {theme.CURRENT.border};
                border-radius: 12px;
            }}
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(4)

        self._title_lbl = make_label(title, 11, color=theme.CURRENT.text_muted)
        lay.addWidget(self._title_lbl)

        self._value_lbl = make_label(value, 24, bold=True)
        lay.addWidget(self._value_lbl)

        self._sub_lbl = make_label(subtitle, 11, color=theme.CURRENT.text_secondary)
        lay.addWidget(self._sub_lbl)

    def set_value(self, value: str):
        self._value_lbl.setText(value)

    def set_sub(self, text: str):
        self._sub_lbl.setText(text)

    def set_sub_color(self, color: str):
        self._sub_lbl.setStyleSheet(f"color: {color}; background: transparent; border: none;")
