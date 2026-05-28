from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox
from PyQt6.QtCore import Qt, QTimer

from core.services.garden_service import get_garden_status, create_new_plant
from ui.widgets.glass_card import GlassCard, make_label
from ui.widgets.garden_canvas import GardenCanvas
from config.settings import PLANT_TYPES
import config.theme as theme


class GardenPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 28, 28, 28)
        lay.setSpacing(16)

        header = QHBoxLayout()
        header.addWidget(make_label("Virtual Garden", 22, bold=True))

        self._plant_combo = QComboBox()
        for key, pt in PLANT_TYPES.items():
            self._plant_combo.addItem(f"{pt['icon']} {pt['name']}", key)
        self._plant_combo.setFixedWidth(150)
        header.addWidget(self._plant_combo)

        btn_plant = QPushButton("Tanam Baru")
        btn_plant.setFixedWidth(120)
        btn_plant.clicked.connect(self._plant_new)
        btn_plant.setCursor(Qt.CursorShape.PointingHandCursor)
        header.addWidget(btn_plant)
        header.addStretch()

        self._stats_label = make_label("", 12, color=theme.CURRENT.text_secondary)
        header.addWidget(self._stats_label)
        lay.addLayout(header)

        # Garden canvas
        self._garden = GardenCanvas()
        self._garden.setMinimumHeight(420)
        lay.addWidget(self._garden)

        # Info card for selected plant
        self._info_card = GlassCard(padding=14)
        self._info_card.setFixedHeight(70)
        self._info_lbl = make_label("Klik tanaman untuk melihat detail", 12, color=theme.CURRENT.text_muted)
        self._info_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._info_card.addWidget(self._info_lbl)
        lay.addWidget(self._info_card)

        lay.addStretch()

        # Auto-refresh every 5 seconds
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(5000)
        self._refresh_timer.timeout.connect(self.refresh)
        self._refresh_timer.start()

    def _plant_new(self):
        plant_type = self._plant_combo.currentData()
        create_new_plant(plant_type)
        self.refresh()

    def refresh(self):
        status = get_garden_status()
        plants = status["plants"]
        total = status["total"]
        full = status["full_grown"]

        self._stats_label.setText(f"{total} tanaman | {full} tumbuh penuh")
        self._garden.refresh()

        # Update selected plant info
        selected = self._garden.selected_plant()
        if selected:
            pt = PLANT_TYPES.get(selected["type"], PLANT_TYPES["tree"])
            stage_names = ["Biji", "Tunas", "Tumbuh", "Mekar", "Dewasa"]
            stage_name = stage_names[min(selected["stage"], 4)]
            stage_icon = pt["stages"][min(selected["stage"], 4)]
            if selected["stage"] < 4:
                self._info_lbl.setText(
                    f"{stage_icon}  {pt['name']} — {stage_name}  |  "
                    f"XP: {selected['xp']}/{selected['xp_required']}  |  "
                    f"Sesi: {selected['session_count']}"
                )
            else:
                self._info_lbl.setText(
                    f"{stage_icon}  {pt['name']} — {stage_name} (Full Grown)  |  "
                    f"Sesi: {selected['session_count']}"
                )
        else:
            self._info_lbl.setText("Klik tanaman untuk melihat detail" if plants else
                                   "Belum ada tanaman. Mulai sesi fokus untuk menanam!")
