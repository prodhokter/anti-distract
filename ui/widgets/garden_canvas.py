import math, random, time
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QRadialGradient, QLinearGradient,
    QFont, QPainterPath,
)

from core.services.garden_service import get_garden_status
from config.settings import PLANT_TYPES
import config.theme as theme


# ── Garden palettes ──────────────────────────────────────────

def _is_dark():
    return theme.CURRENT is theme.DARK


def _garden_colors():
    """Return garden-specific colors derived from current theme."""
    if _is_dark():
        return {
            "sky_top": QColor("#0f1a2e"),
            "sky_mid": QColor("#162038"),
            "sky_bot": QColor("#1a2740"),
            "sun_glow_0": QColor(255, 200, 100, 40),
            "sun_glow_1": QColor(255, 160, 60, 15),
            "sun_glow_2": QColor(255, 100, 30, 0),
            "sun_inner_0": QColor(255, 240, 200),
            "sun_inner_1": QColor(255, 180, 60),
            "sun_inner_2": QColor(255, 120, 20),
            "ground_top": QColor("#1a3a1a"),
            "ground_mid": QColor("#163016"),
            "ground_bot": QColor("#0f200f"),
            "grass_0": QColor("#2d5a2d"),
            "grass_1": QColor("#3a6b3a"),
            "grass_2": QColor("#1a3a1a"),
            "trunk_young": QColor("#6B4226"),
            "trunk_mature": QColor("#8B5E3C"),
            "seed": QColor("#8B6914"),
            "sprout": QColor("#4CAF50"),
            "leaf": QColor("#66BB6A"),
            "stem": QColor("#4CAF50"),
            "mushroom_stem": QColor("#F5E6D3"),
            "particle": QColor(200, 220, 255, 100),
            "flower_center": QColor("#FFD54F"),
            "stars": True,
            "butterflies": False,
        }
    else:
        return {
            "sky_top": QColor("#C8DFFF"),
            "sky_mid": QColor("#DAEAFF"),
            "sky_bot": QColor("#E8F1FF"),
            "sun_glow_0": QColor(255, 215, 0, 50),
            "sun_glow_1": QColor(255, 200, 50, 25),
            "sun_glow_2": QColor(255, 180, 0, 0),
            "sun_inner_0": QColor(255, 255, 220),
            "sun_inner_1": QColor(255, 220, 80),
            "sun_inner_2": QColor(255, 180, 30),
            "ground_top": QColor("#7CCD7C"),
            "ground_mid": QColor("#5DAE5D"),
            "ground_bot": QColor("#3D8E3D"),
            "grass_0": QColor("#4CAF50"),
            "grass_1": QColor("#66BB6A"),
            "grass_2": QColor("#388E3C"),
            "trunk_young": QColor("#8B6914"),
            "trunk_mature": QColor("#A0722F"),
            "seed": QColor("#8B6914"),
            "sprout": QColor("#4CAF50"),
            "leaf": QColor("#81C784"),
            "stem": QColor("#4CAF50"),
            "mushroom_stem": QColor("#FFF8EE"),
            "particle": QColor(255, 255, 255, 120),
            "flower_center": QColor("#FFD54F"),
            "stars": False,
            "butterflies": True,
        }


# ── Flower petal colors (works in both modes) ────────────────

PETAL_COLORS = [
    QColor("#FF80AB"), QColor("#FFAB91"), QColor("#FFF176"),
    QColor("#CE93D8"), QColor("#80DEEA"), QColor("#F48FB1"),
    QColor("#FFE082"), QColor("#A5D6A7"),
]


class GardenCanvas(QWidget):
    """Theme-aware virtual garden with plants, sky, ground, particles, and butterflies."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 400)
        self.setStyleSheet(
            f"background: transparent; border: 1px solid {theme.CURRENT.border}; border-radius: 14px;"
        )

        self._plants = []
        self._time = 0.0
        self._particles = []
        self._butterflies = []
        self._selected_plant = None
        self._init_particles()
        self._init_butterflies()

        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(40)
        self._anim_timer.timeout.connect(self._animate)
        self._anim_timer.start()

        self.setMouseTracking(True)

    def _init_particles(self):
        self._particles = [
            {"x": random.random(), "y": random.random() * 0.7,
             "speed": random.uniform(0.1, 0.4), "size": random.uniform(1.5, 4.0),
             "alpha": random.uniform(0.2, 0.5)} for _ in range(30)
        ]

    def _init_butterflies(self):
        self._butterflies = [
            {"x": random.uniform(0.05, 0.9), "y": random.uniform(0.05, 0.5),
             "dx": random.uniform(0.3, 0.8), "dy": random.uniform(-0.15, 0.15),
             "size": random.uniform(4.0, 8.0),
             "phase": random.uniform(0, 2 * math.pi),
             "color": PETAL_COLORS[i % len(PETAL_COLORS)]}
            for i in range(5)
        ]

    def _animate(self):
        self._time += 0.04
        gc = _garden_colors()

        for p in self._particles:
            p["y"] -= p["speed"] * 0.003
            if p["y"] < 0:
                p["y"] = 0.7 + random.uniform(0, 0.15)
                p["x"] = random.random()

        if gc["butterflies"]:
            for b in self._butterflies:
                b["x"] += b["dx"] * 0.003
                b["y"] += b["dy"] * 0.003 + math.sin(self._time * 1.3 + b["phase"]) * 0.004
                if b["x"] > 1.05: b["x"] = -0.05
                if b["x"] < -0.05: b["x"] = 1.05
                if b["y"] < 0.02: b["y"] = 0.02
                if b["y"] > 0.55: b["y"] = 0.55

        self.update()

    def refresh(self):
        status = get_garden_status()
        self._plants = status["plants"]
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        self._draw_sky(p, w, h)
        self._draw_sun(p, w, h)
        self._draw_ground(p, w, h)
        self._draw_particles(p, w, h)
        self._draw_butterflies(p, w, h)
        self._draw_plants(p, w, h)

        if not self._plants:
            self._draw_empty_state(p, w, h)

        p.end()

    def _draw_sky(self, p: QPainter, w: int, h: int):
        gc = _garden_colors()
        sky_h = int(h * 0.55)

        sky = QLinearGradient(0, 0, 0, sky_h)
        sky.setColorAt(0, gc["sky_top"])
        sky.setColorAt(0.5, gc["sky_mid"])
        sky.setColorAt(1, gc["sky_bot"])
        p.fillRect(0, 0, w, sky_h, sky)

        if gc["stars"]:
            rng = random.Random(42)
            p.setPen(Qt.PenStyle.NoPen)
            for _ in range(40):
                sx = rng.randint(0, w)
                sy = rng.randint(0, int(h * 0.3))
                alpha = 100 + int(80 * (0.5 + 0.5 * math.sin(self._time * 1.5 + sx)))
                star = QColor(255, 255, 255, alpha)
                p.setBrush(star)
                size = rng.uniform(0.8, 2.0)
                p.drawEllipse(QPointF(sx, sy), size, size)

        # Small decorative clouds in light mode
        if not gc["stars"]:
            self._draw_clouds(p, w, h)

    def _draw_clouds(self, p: QPainter, w: int, h: int):
        p.setPen(Qt.PenStyle.NoPen)
        cloud_color = QColor(255, 255, 255, 120)
        p.setBrush(cloud_color)

        clouds = [
            (w * 0.65, h * 0.08, 0.02),
            (w * 0.55, h * 0.18, -0.015),
            (w * 0.75, h * 0.04, 0.01),
        ]
        for base_x, base_y, drift_speed in clouds:
            cx = base_x + math.sin(self._time * 0.3 + base_x * 0.01) * 20
            cy = base_y
            # cloud body - overlapping ellipses
            for ox, oy, r in [(0, 0, 18), (18, -4, 14), (-16, 0, 13), (8, 6, 10), (-10, 4, 11)]:
                p.drawEllipse(QPointF(cx + ox, cy + oy), r, r * 0.7)

    def _draw_sun(self, p: QPainter, w: int, h: int):
        gc = _garden_colors()
        cx, cy = w * 0.2, h * 0.15
        radius = min(w, h) * 0.06

        glow = QRadialGradient(cx, cy, radius * 4)
        glow.setColorAt(0, gc["sun_glow_0"])
        glow.setColorAt(0.3, gc["sun_glow_1"])
        glow.setColorAt(1, gc["sun_glow_2"])
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(glow)
        p.drawEllipse(QPointF(cx, cy), radius * 4, radius * 4)

        sun = QRadialGradient(cx, cy, radius)
        sun.setColorAt(0, gc["sun_inner_0"])
        sun.setColorAt(0.6, gc["sun_inner_1"])
        sun.setColorAt(1, gc["sun_inner_2"])
        p.setBrush(sun)
        p.drawEllipse(QPointF(cx, cy), radius, radius)

    def _draw_ground(self, p: QPainter, w: int, h: int):
        gc = _garden_colors()
        ground_y = int(h * 0.52)
        ground_h = h - ground_y

        gnd = QLinearGradient(0, ground_y, 0, h)
        gnd.setColorAt(0, gc["ground_top"])
        gnd.setColorAt(0.3, gc["ground_mid"])
        gnd.setColorAt(1, gc["ground_bot"])
        p.fillRect(0, ground_y, w, ground_h, gnd)

        # Grass line
        grass = QLinearGradient(0, ground_y - 8, 0, ground_y + 12)
        grass.setColorAt(0, gc["grass_0"])
        grass.setColorAt(0.5, gc["grass_1"])
        grass.setColorAt(1, gc["grass_2"])
        p.fillRect(0, ground_y - 4, w, 16, grass)

        # Grass blades
        rng = random.Random(123)
        p.setPen(Qt.PenStyle.NoPen)
        for x in range(0, w, 8):
            blade_h = rng.randint(6, 18)
            blade_w = 2
            gx = x + rng.randint(-2, 2)
            gy = ground_y - 2

            path = QPainterPath()
            path.moveTo(gx, gy)
            path.quadTo(gx - blade_w, gy - blade_h * 0.6, gx - 1, gy - blade_h)
            path.quadTo(gx, gy - blade_h * 0.7, gx + 1, gy - blade_h)
            path.quadTo(gx + blade_w, gy - blade_h * 0.6, gx, gy)

            shade = rng.randint(80, 160) if _is_dark() else rng.randint(120, 200)
            g = 180 + rng.randint(-20, 40)
            p.setBrush(QColor(shade, g, shade, 200))
            p.drawPath(path)

        # Small flowers scattered in light mode
        if not _is_dark():
            self._draw_ground_flowers(p, w, ground_y)

    def _draw_ground_flowers(self, p: QPainter, w: int, ground_y: int):
        rng = random.Random(77)
        p.setPen(Qt.PenStyle.NoPen)
        for _ in range(12):
            fx = rng.randint(15, w - 15)
            fy = ground_y + rng.randint(5, 30)
            fsize = rng.uniform(2.0, 4.0)
            color = PETAL_COLORS[_ % len(PETAL_COLORS)]
            p.setBrush(color)
            p.drawEllipse(QPointF(fx, fy), fsize, fsize * 0.7)
            p.setBrush(QColor("#FFF9C4"))
            p.drawEllipse(QPointF(fx, fy), fsize * 0.35, fsize * 0.35)

    def _draw_particles(self, p: QPainter, w: int, h: int):
        gc = _garden_colors()
        for pt in self._particles:
            px, py = pt["x"] * w, pt["y"] * h
            color = QColor(
                gc["particle"].red(),
                gc["particle"].green(),
                gc["particle"].blue(),
                int(pt["alpha"] * 255),
            )
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(color)
            p.drawEllipse(QPointF(px, py), pt["size"], pt["size"])

    def _draw_butterflies(self, p: QPainter, w: int, h: int):
        gc = _garden_colors()
        if not gc["butterflies"]:
            return

        for b in self._butterflies:
            bx, by = b["x"] * w, b["y"] * h
            bsize = b["size"]
            wing_angle = math.sin(self._time * 6 + b["phase"]) * 0.6

            p.save()
            p.translate(bx, by)
            p.setPen(Qt.PenStyle.NoPen)

            # Body
            body_color = QColor(60, 40, 20)
            p.setBrush(body_color)
            p.drawEllipse(QPointF(0, 0), 1.5, bsize * 0.35)

            # Wings
            wing_color = QColor(
                b["color"].red(), b["color"].green(), b["color"].blue(), 200
            )
            p.setBrush(wing_color)

            # Left wings
            p.save()
            p.rotate(-20)
            p.scale(1, max(0.1, abs(wing_angle)))
            p.drawEllipse(QPointF(-bsize * 0.35, -bsize * 0.15), bsize * 0.5, bsize * 0.35)
            p.drawEllipse(QPointF(-bsize * 0.3, bsize * 0.2), bsize * 0.35, bsize * 0.25)
            p.restore()

            # Right wings
            p.save()
            p.rotate(20)
            p.scale(1, max(0.1, abs(wing_angle)))
            p.drawEllipse(QPointF(bsize * 0.35, -bsize * 0.15), bsize * 0.5, bsize * 0.35)
            p.drawEllipse(QPointF(bsize * 0.3, bsize * 0.2), bsize * 0.35, bsize * 0.25)
            p.restore()

            p.restore()

    def _draw_plants(self, p: QPainter, w: int, h: int):
        if not self._plants:
            return

        n = len(self._plants)
        spacing = min(140, w // max(n, 1))
        start_x = (w - (n - 1) * spacing) // 2
        ground_y = int(h * 0.52)

        for i, plant in enumerate(self._plants):
            px = start_x + i * spacing
            py = ground_y

            pt = PLANT_TYPES.get(plant["type"], PLANT_TYPES["tree"])
            stage = min(plant["stage"], 4)
            stage_name = ["Biji", "Tunas", "Tumbuh", "Mekar", "Dewasa"][stage]

            self._draw_single_plant(p, px, py, plant, pt, stage)

            # Progress bar
            self._draw_plant_progress(p, px, py, plant)

            # Plant info
            C = theme.CURRENT
            p.setPen(QColor(C.text_secondary))
            p.setFont(QFont("Segoe UI", 9))
            p.drawText(QRectF(px - 50, py - 20, 100, 16), Qt.AlignmentFlag.AlignHCenter, pt["name"])
            p.setFont(QFont("Segoe UI", 8))
            p.setPen(QColor(C.text_muted))
            p.drawText(QRectF(px - 50, py - 8, 100, 14), Qt.AlignmentFlag.AlignHCenter, stage_name)

            # Click indicator
            if plant == self._selected_plant:
                p.setPen(QPen(QColor(C.accent), 2, Qt.PenStyle.DashLine))
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawRoundedRect(QRectF(px - 52, py - 140, 104, 170), 10, 10)

    def _draw_single_plant(self, p: QPainter, px: int, py: int, plant: dict, pt: dict, stage: int):
        base_size = 12 + stage * 8
        wobble = math.sin(self._time * 2 + px * 0.05) * 2

        plant_type = pt["type"]
        if plant_type == "tree":
            self._draw_tree(p, px, py, base_size, stage, wobble)
        elif plant_type == "flower":
            self._draw_flower(p, px, py, base_size, stage, wobble)
        elif plant_type == "cactus":
            self._draw_cactus(p, px, py, base_size, stage)
        elif plant_type == "mushroom":
            self._draw_mushroom(p, px, py, base_size, stage)
        elif plant_type == "herb":
            self._draw_herb(p, px, py, base_size, stage, wobble)
        else:
            self._draw_tree(p, px, py, base_size, stage, wobble)

    def _draw_tree(self, p: QPainter, px: int, py: int, size: int, stage: int, wobble: float):
        gc = _garden_colors()

        if stage == 0:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(gc["seed"])
            p.drawEllipse(QPointF(px, py - 6), 5, 4)
            p.setPen(QPen(gc["sprout"], 2))
            p.drawLine(QPointF(px, py - 8), QPointF(px + wobble, py - 16))
            return

        # Trunk
        trunk_w = max(3, stage + 2)
        trunk_h = 20 + stage * 15
        trunk_color = gc["trunk_young"] if stage < 3 else gc["trunk_mature"]
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(trunk_color)
        p.drawRoundedRect(QRectF(px - trunk_w / 2, py - trunk_h, trunk_w, trunk_h), 2, 2)

        # Canopy
        canopy_y = py - trunk_h - size * 0.6
        canopy_size = size * (0.6 + stage * 0.3)

        green = QColor(40 + stage * 30, 130 + stage * 20, 40 + stage * 15)
        dark_green = QColor(20 + stage * 20, 80 + stage * 15, 20 + stage * 10)

        for i in range(2 if stage < 3 else 3):
            seed = stage * 7 + i
            cx = px + random.Random(seed).uniform(-canopy_size * 0.4, canopy_size * 0.4)
            cy = canopy_y + random.Random(stage * 11 + i).uniform(-canopy_size * 0.3, canopy_size * 0.3)
            cs = canopy_size * random.Random(stage * 13 + i).uniform(0.7, 1.0)
            grad = QRadialGradient(cx, cy, cs)
            grad.setColorAt(0, green.lighter(110))
            grad.setColorAt(1, dark_green)
            p.setBrush(grad)
            p.drawEllipse(QPointF(cx + wobble, cy), cs, cs * 0.85)

    def _draw_flower(self, p: QPainter, px: int, py: int, size: int, stage: int, wobble: float):
        gc = _garden_colors()

        if stage == 0:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(gc["seed"])
            p.drawEllipse(QPointF(px, py - 5), 4, 3)
            p.setPen(QPen(gc["sprout"], 1.5))
            p.drawLine(QPointF(px, py - 7), QPointF(px + wobble, py - 14))
            return

        # Stem
        stem_h = 15 + stage * 12
        p.setPen(QPen(gc["stem"], max(2, stage)))
        p.drawLine(QPointF(px, py - 3), QPointF(px + wobble, py - stem_h))

        if stage >= 2:
            # Leaf
            leaf_path = QPainterPath()
            lx = px + 6
            ly = py - stem_h * 0.5
            leaf_path.moveTo(px, ly)
            leaf_path.quadTo(lx, ly - 10, lx + 4, ly - 2)
            leaf_path.quadTo(lx + 2, ly + 4, px + 1, ly + 6)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(gc["leaf"])
            p.drawPath(leaf_path)

        if stage >= 2:
            # Petals
            petal_count = 5 if stage >= 4 else 4
            px_center = px + wobble
            py_center = py - stem_h
            petal_size = 6 + stage

            for i in range(petal_count):
                angle = (i / petal_count) * 2 * math.pi + math.sin(self._time * 2 + i) * 0.15
                cx = px_center + math.cos(angle) * petal_size * 0.5
                cy = py_center + math.sin(angle) * petal_size * 0.5
                p.setBrush(PETAL_COLORS[i % len(PETAL_COLORS)])
                p.setPen(Qt.PenStyle.NoPen)
                p.drawEllipse(QPointF(cx, cy), petal_size * 0.55, petal_size * 0.55)

            # Center
            p.setBrush(gc["flower_center"])
            p.drawEllipse(QPointF(px_center, py_center), petal_size * 0.3, petal_size * 0.3)

    def _draw_cactus(self, p: QPainter, px: int, py: int, size: int, stage: int):
        body_w = 10 + stage * 3
        body_h = 20 + stage * 10
        body_color = QColor(80 + stage * 20, 160 + stage * 15, 80)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(body_color)
        p.drawRoundedRect(QRectF(px - body_w / 2, py - body_h, body_w, body_h), 5, 5)

        if stage >= 2:
            arm_color = QColor(60 + stage * 25, 140 + stage * 15, 60)
            p.setBrush(arm_color)
            p.drawRoundedRect(QRectF(px - body_w / 2 - 10, py - body_h * 0.7, 10, 6), 3, 3)
            p.drawRoundedRect(QRectF(px - body_w / 2 - 10, py - body_h * 0.7 - 10, 6, 10), 3, 3)
            if stage >= 3:
                p.drawRoundedRect(QRectF(px + body_w / 2, py - body_h * 0.5, 10, 6), 3, 3)
                p.drawRoundedRect(QRectF(px + body_w / 2 + 4, py - body_h * 0.5 - 12, 6, 12), 3, 3)

        if stage >= 4:
            p.setBrush(PETAL_COLORS[0])
            p.drawEllipse(QPointF(px, py - body_h - 4), 5, 5)
            p.setBrush(QColor("#FFD54F"))
            p.drawEllipse(QPointF(px, py - body_h - 4), 3, 3)

    def _draw_mushroom(self, p: QPainter, px: int, py: int, size: int, stage: int):
        gc = _garden_colors()
        stem_h = 10 + stage * 6
        cap_w = 10 + stage * 5
        cap_h = 8 + stage * 4

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(gc["mushroom_stem"])
        p.drawRoundedRect(QRectF(px - 3, py - stem_h - cap_h * 0.3, 6, stem_h), 2, 2)

        cap_color = QColor(200 + stage * 10, 80 - stage * 10, 50 + stage * 5)
        p.setBrush(cap_color)
        path = QPainterPath()
        path.moveTo(px - cap_w, py - stem_h)
        path.quadTo(px, py - stem_h - cap_h - 4, px + cap_w, py - stem_h)
        path.quadTo(px + cap_w, py - stem_h - cap_h * 0.4, px + cap_w * 0.5, py - stem_h + 2)
        path.quadTo(px, py - stem_h + 6, px - cap_w * 0.5, py - stem_h + 2)
        path.quadTo(px - cap_w, py - stem_h - cap_h * 0.4, px - cap_w, py - stem_h)
        p.drawPath(path)

        if stage >= 2:
            spots_color = QColor(255, 255, 255, 180)
            p.setBrush(spots_color)
            for sp in [(px - cap_w * 0.3, py - stem_h - cap_h * 0.6),
                        (px + cap_w * 0.15, py - stem_h - cap_h * 0.7),
                        (px + cap_w * 0.3, py - stem_h - cap_h * 0.3)]:
                p.drawEllipse(QPointF(*sp), 3, 2.5)

    def _draw_herb(self, p: QPainter, px: int, py: int, size: int, stage: int, wobble: float):
        leaf_count = 3 + stage
        for i in range(leaf_count):
            angle = (i / leaf_count) * math.pi * 0.8 - math.pi * 0.4
            length = (8 + stage * 5) * (0.7 + 0.3 * (i / leaf_count))
            ex = px + math.cos(angle) * length + wobble
            ey = py - abs(math.sin(angle)) * length

            leaf_path = QPainterPath()
            leaf_path.moveTo(px, py - 3)
            cx = px + math.cos(angle) * length * 0.6
            cy = py - abs(math.sin(angle)) * length * 0.5
            leaf_path.quadTo(cx, cy, ex, ey)
            leaf_path.quadTo(cx + 3, cy + 5, px, py - 1)

            shade = QColor(60 + stage * 20, 160 + stage * 10, 50 + stage * 10)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(shade)
            p.drawPath(leaf_path)

    def _draw_plant_progress(self, p: QPainter, px: int, py: int, plant: dict):
        if plant["stage"] >= 4:
            return

        C = theme.CURRENT
        bar_w, bar_h = 60, 5
        bx, by = px - bar_w / 2, py + 20

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(C.progress_bg))
        p.drawRoundedRect(QRectF(bx, by, bar_w, bar_h), 2, 2)

        progress = min(1.0, plant["xp"] / plant["xp_required"]) if plant["xp_required"] > 0 else 0
        fill_w = bar_w * progress
        p.setBrush(QColor(C.accent))
        p.drawRoundedRect(QRectF(bx, by, fill_w, bar_h), 2, 2)

        p.setPen(QColor(C.text_muted))
        p.setFont(QFont("Segoe UI", 7))
        p.drawText(QRectF(bx, by + 7, bar_w, 12), Qt.AlignmentFlag.AlignHCenter,
                   f"{plant['xp']}/{plant['xp_required']}")

    def _draw_empty_state(self, p: QPainter, w: int, h: int):
        C = theme.CURRENT
        p.setPen(QColor(C.text_muted))
        p.setFont(QFont("Segoe UI", 16))
        p.drawText(QRectF(0, h * 0.32, w, 30), Qt.AlignmentFlag.AlignHCenter,
                   "Belum ada tanaman")
        p.setFont(QFont("Segoe UI", 60))
        p.drawText(QRectF(0, h * 0.40, w, 70), Qt.AlignmentFlag.AlignHCenter, "🌱")

        p.setFont(QFont("Segoe UI", 12))
        p.drawText(QRectF(0, h * 0.60, w, 24), Qt.AlignmentFlag.AlignHCenter,
                   "Mulai sesi fokus untuk menanam pohon pertama!")

    def mousePressEvent(self, event):
        if not self._plants:
            return
        w = self.width()
        n = len(self._plants)
        spacing = min(140, w // max(n, 1))
        start_x = (w - (n - 1) * spacing) // 2

        for i, plant in enumerate(self._plants):
            px = start_x + i * spacing
            if abs(event.pos().x() - px) < 52 and event.pos().y() > self.height() * 0.3:
                self._selected_plant = plant if self._selected_plant != plant else None
                self.update()
                return
        self._selected_plant = None
        self.update()

    def selected_plant(self) -> dict | None:
        return self._selected_plant
