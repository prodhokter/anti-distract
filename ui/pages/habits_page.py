from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QCheckBox, QComboBox, QScrollArea, QFrame,
)
from PyQt6.QtCore import Qt

from core.repositories.session_repo import (
    get_habits, create_habit, toggle_habit, get_today_habit_completions,
    get_today_intention, set_daily_intention, complete_today_intention,
    add_xp,
)
from config.settings import XP_HABIT, XP_INTENTION
from ui.widgets.glass_card import GlassCard, make_label
import config.theme as theme

FREQUENCIES = ["daily", "weekly", "weekdays"]
FREQ_LABELS = {"daily": "Harian", "weekly": "Mingguan", "weekdays": "Hari Kerja"}


class HabitsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 28, 28, 28)
        lay.setSpacing(16)

        lay.addWidget(make_label("Kebiasaan & Intensi", 22, bold=True))

        # Daily intention card
        intention_card = GlassCard(padding=16)
        intention_card.addWidget(make_label("Intensi Hari Ini", 13, bold=True))
        int_row = QHBoxLayout()
        self._intention_input = QLineEdit()
        self._intention_input.setPlaceholderText("Apa tujuan utamamu hari ini?")
        int_row.addWidget(self._intention_input)
        btn_set = QPushButton("Set")
        btn_set.setFixedWidth(70)
        btn_set.clicked.connect(self._set_intention)
        btn_set.setCursor(Qt.CursorShape.PointingHandCursor)
        int_row.addWidget(btn_set)
        intention_card.addLayout(int_row)
        self._intention_status = make_label("", 12, color=theme.CURRENT.text_secondary)
        intention_card.addWidget(self._intention_status)
        lay.addWidget(intention_card)

        # Add habit
        add_card = GlassCard(padding=14)
        add_row = QHBoxLayout()
        self._habit_input = QLineEdit()
        self._habit_input.setPlaceholderText("Nama kebiasaan baru...")
        add_row.addWidget(self._habit_input)

        self._freq_combo = QComboBox()
        for f in FREQUENCIES:
            self._freq_combo.addItem(FREQ_LABELS[f], f)
        self._freq_combo.setFixedWidth(110)
        add_row.addWidget(self._freq_combo)

        btn_add = QPushButton("Tambah")
        btn_add.setFixedWidth(90)
        btn_add.clicked.connect(self._add_habit)
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        add_row.addWidget(btn_add)
        add_card.addLayout(add_row)
        lay.addWidget(add_card)

        # Habits list
        self._habits_container = QWidget()
        self._habits_lay = QVBoxLayout(self._habits_container)
        self._habits_lay.setContentsMargins(0, 0, 0, 0)
        self._habits_lay.setSpacing(8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._habits_container)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QWidget#qt_scrollarea_viewport {{ background: transparent; }}
        """)
        lay.addWidget(scroll)

    def _set_intention(self):
        title = self._intention_input.text().strip()
        if title:
            set_daily_intention(title)
            self._intention_input.clear()
            self.refresh()

    def _add_habit(self):
        name = self._habit_input.text().strip()
        if name:
            freq = self._freq_combo.currentData()
            create_habit(name, frequency=freq)
            self._habit_input.clear()
            self.refresh()

    def refresh(self):
        # Intention
        intention = get_today_intention()
        if intention:
            status = "Selesai" if intention.get("completed") else "Belum selesai"
            color = theme.CURRENT.success if intention.get("completed") else theme.CURRENT.warning
            self._intention_status.setText(f"{intention['title']} — {status}")
            self._intention_status.setStyleSheet(f"color: {color}; background: transparent; border: none;")
        else:
            self._intention_status.setText("Belum ada intensi hari ini")
            self._intention_status.setStyleSheet(f"color: {theme.CURRENT.text_muted}; background: transparent; border: none;")

        # Habits
        while self._habits_lay.count():
            item = self._habits_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        habits = get_habits()
        completions = get_today_habit_completions()

        if not habits:
            self._habits_lay.addWidget(make_label("Belum ada kebiasaan. Tambahkan di atas!", 12, color=theme.CURRENT.text_muted))
            return

        for h in habits:
            done = h["id"] in completions
            card = GlassCard(padding=10)
            row = QHBoxLayout()
            row.setContentsMargins(4, 4, 4, 4)

            chk = QCheckBox()
            chk.setChecked(done)
            chk.toggled.connect(lambda checked, hid=h["id"]: self._toggle(hid))
            row.addWidget(chk)

            freq_label = FREQ_LABELS.get(h["frequency"], "Harian")
            info = make_label(f"{h['name']}", 13, bold=done)
            if done:
                info.setStyleSheet(f"color: {theme.CURRENT.text_muted}; text-decoration: line-through; background: transparent; border: none;")
            row.addWidget(info)
            row.addStretch()
            row.addWidget(make_label(freq_label, 10, color=theme.CURRENT.text_muted))
            card.addLayout(row)
            self._habits_lay.addWidget(card)

    def _toggle(self, habit_id: str):
        completed = toggle_habit(habit_id)
        if completed:
            add_xp(XP_HABIT)
        self.refresh()
