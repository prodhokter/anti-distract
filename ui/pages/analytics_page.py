import json
import datetime
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
import pyqtgraph as pg

from core.repositories.session_repo import (
    get_week_stats, get_peak_hours_data, get_user_progress,
    get_today_stats, get_achievements, get_category_stats,
    get_focus_trend,
)
import core.repositories.settings_repo as settings_repo
from core.services.export_service import export_all
from ui.widgets.glass_card import GlassCard, make_label, StatCard
from ui.widgets.bar_chart import WeekBarChart
import config.theme as theme


class AnalyticsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 28, 28, 28)
        lay.setSpacing(16)

        header = QHBoxLayout()
        header.addWidget(make_label("Analitik", 22, bold=True))
        header.addStretch()

        btn_export = QPushButton("Export Data")
        btn_export.setObjectName("secondary")
        btn_export.setFixedSize(130, 36)
        btn_export.clicked.connect(self._export_data)
        btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        header.addWidget(btn_export)
        lay.addLayout(header)

        # Stats row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)
        self._card_total_h = StatCard("Total Jam Fokus", "0j", "sepanjang waktu")
        self._card_avg = StatCard("Rata-rata Harian", "0 mnt", "7 hari terakhir")
        self._card_best = StatCard("Hari Terbaik", "--", "")
        self._card_level = StatCard("Level", "1", "0 XP")
        for c in [self._card_total_h, self._card_avg, self._card_best, self._card_level]:
            stats_row.addWidget(c)
        lay.addLayout(stats_row)

        # Weekly chart
        chart_card = GlassCard(padding=18)
        chart_card.addWidget(make_label("Fokus 7 Hari Terakhir", 13, bold=True))
        self._week_chart = WeekBarChart()
        chart_card.addWidget(self._week_chart)
        lay.addWidget(chart_card)

        # Trend chart (30 days)
        trend_card = GlassCard(padding=18)
        trend_card.addWidget(make_label("Tren Fokus 30 Hari", 13, bold=True))
        self._trend_widget = pg.PlotWidget()
        self._trend_widget.setMinimumHeight(180)
        self._trend_widget.setBackground(theme.CURRENT.bg_secondary)
        self._trend_widget.getAxis("left").setPen(theme.CURRENT.text_muted)
        self._trend_widget.getAxis("bottom").setPen(theme.CURRENT.text_muted)
        self._trend_widget.getAxis("left").setTextPen(theme.CURRENT.text_secondary)
        self._trend_widget.getAxis("bottom").setTextPen(theme.CURRENT.text_secondary)
        self._trend_widget.showGrid(x=True, y=True, alpha=0.15)
        trend_card.addWidget(self._trend_widget)
        lay.addWidget(trend_card)

        # Bottom row: category breakdown + peak hours
        bottom = QHBoxLayout()
        bottom.setSpacing(14)

        # Category donut
        cat_card = GlassCard(padding=18)
        cat_card.addWidget(make_label("Kategori Fokus", 13, bold=True))
        self._cat_widget = pg.PlotWidget()
        self._cat_widget.setMinimumHeight(200)
        self._cat_widget.setMaximumWidth(400)
        self._cat_widget.setBackground(theme.CURRENT.bg_secondary)
        self._cat_widget.getAxis("left").hide()
        self._cat_widget.getAxis("bottom").hide()
        cat_card.addWidget(self._cat_widget)
        bottom.addWidget(cat_card)

        # Peak hours heatmap
        heatmap_card = GlassCard(padding=18)
        heatmap_card.addWidget(make_label("Jam Produktif (30 hari terakhir)", 13, bold=True))
        self._heatmap_lay = QHBoxLayout()
        self._heatmap_lay.setSpacing(6)
        heatmap_card.addLayout(self._heatmap_lay)
        bottom.addWidget(heatmap_card)

        lay.addLayout(bottom)

        # Achievements
        ach_card = GlassCard(padding=18)
        ach_card.addWidget(make_label("Achievements", 13, bold=True))
        self._ach_grid = QHBoxLayout()
        self._ach_grid.setSpacing(8)
        ach_card.addLayout(self._ach_grid)
        lay.addWidget(ach_card)

        lay.addStretch()

    def _export_data(self):
        try:
            result = export_all()
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self, "Export Berhasil",
                f"Data diexport ke:\n\n"
                f"Sesi: {result['sessions']}\n"
                f"Kebiasaan: {result['habits']}",
            )
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Export Gagal", str(e))

    def refresh(self):
        goal = int(settings_repo.get_setting("daily_goal_minutes", "120"))
        user = get_user_progress()
        week = get_week_stats(7)
        today = get_today_stats()

        total_h = user.get("total_minutes", 0) / 60
        self._card_total_h.set_value(f"{total_h:.0f}j")
        self._card_total_h.set_sub("sepanjang waktu")

        if week:
            avg = sum(r["total_minutes"] for r in week) / len(week)
            best = max(week, key=lambda r: r["total_minutes"])
            self._card_avg.set_value(f"{int(avg)} mnt")
            self._card_best.set_value(f"{int(best['total_minutes'])} mnt")
            self._card_best.set_sub(best["date"])
        else:
            self._card_avg.set_value("0 mnt")
            self._card_best.set_value("--")

        xp = user.get("total_xp", 0)
        self._card_level.set_value(str(user.get("level", 1)))
        self._card_level.set_sub(f"{xp} XP")

        self._week_chart.set_data(week, goal)

        # Trend chart
        self._draw_trend()

        # Category chart
        self._draw_categories()

        # Heatmap
        self._draw_heatmap()

        # Achievements
        self._draw_achievements(user)

    def _draw_trend(self):
        self._trend_widget.clear()
        trend = get_focus_trend(30)

        if not trend:
            return

        dates = [r["date"] for r in trend]
        minutes = [r["total_minutes"] for r in trend]
        x_vals = list(range(len(dates)))

        pen = pg.mkPen(color=theme.CURRENT.accent, width=2)
        r, g, b = int(theme.CURRENT.accent[1:3], 16), int(theme.CURRENT.accent[3:5], 16), int(theme.CURRENT.accent[5:7], 16)
        brush = pg.mkBrush(r, g, b, 40)

        self._trend_widget.plot(x_vals, minutes, pen=pen, fillLevel=0, brush=brush)

        axis = self._trend_widget.getAxis("bottom")
        ticks = [(i, d[-5:]) for i, d in enumerate(dates) if i % 5 == 0]
        axis.setTicks([ticks])

        self._trend_widget.setLabel("left", "Menit")

    def _draw_categories(self):
        self._cat_widget.clear()
        stats = get_category_stats(30)

        if not stats:
            return

        total = sum(s["total_minutes"] for s in stats)
        if total == 0:
            return

        from config.theme import CATEGORY_PALETTE
        colors_list = CATEGORY_PALETTE
        current_angle = 90
        bar_height = 0.6

        for i, cat in enumerate(stats):
            pct = cat["total_minutes"] / total
            span = pct * 360
            color = colors_list[i % len(colors_list)]

            bar = pg.BarGraphItem(
                x=[i], height=[cat["total_minutes"]],
                width=0.6, brush=color,
            )
            self._cat_widget.addItem(bar)

        # Replace bar chart with a donut-like visual using multiple bar sets
        # Actually use a simpler approach: horizontal bars with labels
        self._cat_widget.clear()

        cat_names = [s["category"][:8] for s in stats]
        cat_mins = [s["total_minutes"] for s in stats]
        y_vals = list(range(len(stats)))

        bars = pg.BarGraphItem(
            x=cat_mins, y=y_vals, height=0.5, width=0,
            brushes=[colors_list[i % len(colors_list)] for i in range(len(stats))],
        )
        self._cat_widget.addItem(bars)

        axis_left = self._cat_widget.getAxis("left")
        axis_left.setTicks([[(i, name) for i, name in enumerate(cat_names)]])
        axis_left.setStyle(showValues=True)
        axis_left.setPen(theme.CURRENT.text_muted)
        axis_left.setTextPen(theme.CURRENT.text_secondary)

        axis_bottom = self._cat_widget.getAxis("bottom")
        axis_bottom.setPen(theme.CURRENT.text_muted)
        axis_bottom.setTextPen(theme.CURRENT.text_secondary)
        axis_bottom.setLabel("Menit")
        self._cat_widget.showGrid(x=True, y=False, alpha=0.1)

    def _draw_heatmap(self):
        while self._heatmap_lay.count():
            item = self._heatmap_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        peak_data = get_peak_hours_data(30)
        max_min = max((r["total_minutes"] for r in peak_data), default=1)

        for entry in peak_data:
            hour = entry["hour"]
            mins = entry["total_minutes"]
            intensity = int(mins / max_min * 100) if max_min > 0 else 0

            bar = GlassCard(padding=4)
            bar.setFixedWidth(36)
            inner = QVBoxLayout()
            inner.setContentsMargins(0, 0, 0, 0)

            if intensity > 0:
                h = max(4, int(intensity * 0.8))
                spacer_top = 80 - h
                if spacer_top > 0:
                    inner.addSpacing(spacer_top)
                fill = QLabel()
                fill.setFixedSize(28, h)
                fill.setStyleSheet(f"background: {theme.CURRENT.accent}; border-radius: 4px;")
                inner.addWidget(fill)
            else:
                inner.addSpacing(80)

            lbl = make_label(f"{hour:02d}", 9, color=theme.CURRENT.text_muted)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            inner.addWidget(lbl)
            bar.addLayout(inner)
            self._heatmap_lay.addWidget(bar)

    def _draw_achievements(self, user: dict):
        while self._ach_grid.count():
            item = self._ach_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        all_ach = get_achievements()
        unlocked = json.loads(user.get("achievements_json", "[]"))

        for ach in all_ach[:8]:
            locked = ach["key"] not in unlocked
            ach_card = GlassCard(padding=8)
            ach_card.setFixedSize(100, 90)
            icon = make_label("🔒" if locked else ach["icon"], 24)
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ach_card.addWidget(icon)
            name = make_label(ach["name"], 9, bold=True, color=theme.CURRENT.text if not locked else theme.CURRENT.text_muted)
            ach_card.addWidget(name)
            xp_txt = make_label(f"+{ach['xp_reward']} XP", 9, color=theme.CURRENT.accent if not locked else theme.CURRENT.text_muted)
            ach_card.addWidget(xp_txt)
            self._ach_grid.addWidget(ach_card)
