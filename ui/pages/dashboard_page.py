from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt

import core.repositories.session_repo as repo
import core.repositories.settings_repo as settings_repo
from core.services.focus_service import FocusService, State
from ui.widgets.glass_card import GlassCard, StatCard, make_label
from ui.widgets.bar_chart import WeekBarChart
import config.theme as theme


class DashboardPage(QWidget):
    def __init__(self, focus: FocusService, parent=None):
        super().__init__(parent)
        self.focus = focus
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 28, 28, 28)
        lay.setSpacing(20)

        # Header
        header = QHBoxLayout()
        title = make_label("Dashboard", 22, bold=True)
        header.addWidget(title)
        header.addStretch()

        self._daily_intention_lbl = make_label("", 13, color=theme.CURRENT.accent)
        header.addWidget(self._daily_intention_lbl)
        lay.addLayout(header)

        # Stat cards row
        cards = QHBoxLayout()
        cards.setSpacing(14)

        self._card_study = StatCard("Total Belajar Hari Ini", "0 mnt", "/ 120 mnt")
        self._card_away = StatCard("Pergi dari Layar", "0", "kali hari ini")
        self._card_blocked = StatCard("Tab Diblokir", "0", "kali hari ini")
        self._card_streak = StatCard("Streak", "0", "hari berturut-turut")
        self._card_score = StatCard("Skor Produktivitas", "—", "/100")

        for c in [self._card_study, self._card_away, self._card_blocked, self._card_streak, self._card_score]:
            cards.addWidget(c)
        lay.addLayout(cards)

        # Progress bar
        progress_card = GlassCard(padding=18)
        progress_card.addWidget(make_label("Target Harian", 12, color=theme.CURRENT.text_secondary))
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setFixedHeight(18)
        self._progress.setTextVisible(True)
        progress_card.addWidget(self._progress)
        self._progress_label = make_label("0 / 120 mnt (0%)", 11, color=theme.CURRENT.text_muted)
        progress_card.addWidget(self._progress_label)
        lay.addWidget(progress_card)

        # Weekly chart
        chart_card = GlassCard(padding=18)
        chart_card.addWidget(make_label("7 Hari Terakhir", 13, bold=True))
        self._week_chart = WeekBarChart()
        chart_card.addWidget(self._week_chart)
        lay.addWidget(chart_card)

        lay.addStretch()

    def refresh(self):
        goal = int(settings_repo.get_setting("daily_goal_minutes", "120"))
        stats = repo.get_today_stats()
        today_m = stats["total_seconds"] // 60
        pct = min(100, int(today_m / goal * 100)) if goal else 0

        self._card_study.set_value(f"{today_m} mnt")
        self._card_study.set_sub(f"/ {goal} mnt")
        self._card_away.set_value(str(stats["away_count"]))
        self._card_blocked.set_value(str(stats["blocked_count"]))

        from core.repositories.session_repo import get_user_progress
        user = get_user_progress()
        self._card_streak.set_value(str(user.get("current_streak", 0)))

        self._progress.setValue(pct)
        self._progress_label.setText(f"{today_m} / {goal} mnt ({pct}%)")

        color = theme.CURRENT.success if pct >= 100 else theme.CURRENT.accent
        text_color = "#ffffff" if pct >= 100 else theme.CURRENT.text
        self._progress.setStyleSheet(f"""
            QProgressBar::chunk {{ background-color: {color}; border-radius: 6px; }}
            QProgressBar {{ color: {text_color}; }}
        """)

        intention = repo.get_today_intention()
        if intention:
            self._daily_intention_lbl.setText(f"Fokus: {intention['title']}")
        else:
            self._daily_intention_lbl.setText("")

        # Productivity score
        w = self.window()
        if w and hasattr(w, 'get_productivity_score'):
            score = w.get_productivity_score()
            self._card_score.set_value(str(score["total"]))
            self._card_score.set_sub(f"Nilai {score['grade']} / 100")

        week = repo.get_week_stats(7)
        self._week_chart.set_data(week, goal)
