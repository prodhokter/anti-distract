from dataclasses import dataclass


# ── Design Tokens ──────────────────────────────────────────

RADIUS_SM = 6
RADIUS_MD = 10
RADIUS_LG = 16
SPACING_XS = 4
SPACING_SM = 8
SPACING_MD = 16
SPACING_LG = 24
SPACING_XL = 32

# Category chart palette (used in analytics)
CATEGORY_PALETTE = [
    "#6c63ff", "#ff6b9d", "#ffa726", "#43b89c", "#42a5f5",
    "#ab47bc", "#ef5350", "#26c6da",
]


@dataclass
class ThemeColors:
    bg: str
    bg_secondary: str
    panel: str
    border: str
    accent: str
    accent_hover: str
    accent_pressed: str
    accent_secondary: str
    accent_tertiary: str
    danger: str
    danger_hover: str
    success: str
    warning: str
    text: str
    text_secondary: str
    text_muted: str
    sidebar_bg: str
    card_bg: str
    input_bg: str
    progress_bg: str
    gradient_start: str
    gradient_end: str
    overlay_bg: str
    overlay_critical: str
    overlay_warning: str
    overlay_info: str


# ── Light Theme (DEFAULT) ──────────────────────────────────

LIGHT = ThemeColors(
    bg="#f5f7fb",
    bg_secondary="#eef1f6",
    panel="#ffffff",
    border="#cdd5e1",
    accent="#6c63ff",
    accent_hover="#5a53e0",
    accent_pressed="#4a44cc",
    accent_secondary="#e8547d",
    accent_tertiary="#f59e0b",
    danger="#e11d48",
    danger_hover="#be123c",
    success="#10b981",
    warning="#f59e0b",
    text="#1e293b",
    text_secondary="#475569",
    text_muted="#64748b",
    sidebar_bg="#ffffff",
    card_bg="#ffffff",
    input_bg="#f8fafc",
    progress_bg="#e2e8f0",
    gradient_start="#6c63ff",
    gradient_end="#e8547d",
    overlay_bg="rgba(245, 247, 251, 232)",
    overlay_critical="rgba(254, 226, 226, 240)",
    overlay_warning="rgba(254, 243, 199, 240)",
    overlay_info="rgba(224, 231, 255, 240)",
)

# ── Dark Theme ─────────────────────────────────────────────

DARK = ThemeColors(
    bg="#080b12",
    bg_secondary="#0d1117",
    panel="#131824",
    border="#1e2433",
    accent="#7c74ff",
    accent_hover="#8c84ff",
    accent_pressed="#6c63ff",
    accent_secondary="#ff7a9a",
    accent_tertiary="#ffb74d",
    danger="#ff6584",
    danger_hover="#ff7a9a",
    success="#43b89c",
    warning="#f9a825",
    text="#e2e8f0",
    text_secondary="#94a3b8",
    text_muted="#64748b",
    sidebar_bg="#0a0e16",
    card_bg="#131824",
    input_bg="#0d1117",
    progress_bg="#1e2433",
    gradient_start="#7c74ff",
    gradient_end="#ff7a9a",
    overlay_bg="rgba(10, 14, 22, 220)",
    overlay_critical="rgba(180, 20, 30, 220)",
    overlay_warning="rgba(180, 120, 0, 200)",
    overlay_info="rgba(20, 20, 40, 200)",
)

# ── Current state (LIGHT = default) ────────────────────────

CURRENT: ThemeColors = LIGHT


def set_theme(is_dark: bool):
    global CURRENT
    CURRENT = DARK if is_dark else LIGHT


def build_stylesheet(colors: ThemeColors) -> str:
    # Determine if light or dark for conditional styling
    is_light = colors.bg.startswith("#f") or "255" in colors.overlay_bg
    secondary_btn_bg = "#e2e8f0" if is_light else colors.border
    secondary_btn_hover = "#cbd5e1" if is_light else colors.text_muted

    return f"""
    QMainWindow, QWidget {{
        background-color: {colors.bg};
        color: {colors.text};
        font-family: 'Segoe UI', 'Inter', sans-serif;
        font-size: 13px;
    }}

    QTabWidget::pane {{
        border: 1px solid {colors.border};
        background: {colors.panel};
        border-radius: {RADIUS_MD}px;
    }}
    QTabBar::tab {{
        background: transparent;
        color: {colors.text_secondary};
        padding: 10px 24px;
        border: none;
        font-size: 13px;
    }}
    QTabBar::tab:selected {{
        color: {colors.text};
        border-bottom: 2px solid {colors.accent};
    }}

    QPushButton {{
        background-color: {colors.accent};
        color: white;
        border: none;
        border-radius: {RADIUS_SM}px;
        padding: 10px 20px;
        font-size: 13px;
        font-weight: 600;
    }}
    QPushButton:hover {{ background-color: {colors.accent_hover}; }}
    QPushButton:pressed {{ background-color: {colors.accent_pressed}; }}

    QPushButton#danger {{
        background-color: {colors.danger};
    }}
    QPushButton#danger:hover {{ background-color: {colors.danger_hover}; }}

    QPushButton#secondary {{
        background-color: {secondary_btn_bg};
        color: {colors.text};
        border: 1px solid {colors.border};
    }}
    QPushButton#secondary:hover {{ background-color: {secondary_btn_hover}; }}

    QPushButton#ghost {{
        background-color: transparent;
        color: {colors.text_secondary};
        padding: 6px 12px;
    }}
    QPushButton#ghost:hover {{
        background-color: {colors.border};
        color: {colors.text};
    }}

    QPushButton#success {{
        background-color: {colors.success};
        color: white;
    }}
    QPushButton#success:hover {{ background-color: {colors.accent_hover}; }}

    QProgressBar {{
        background-color: {colors.progress_bg};
        border-radius: {RADIUS_SM}px;
        height: 12px;
        text-align: center;
        color: {colors.text};
        font-size: 11px;
        border: none;
    }}
    QProgressBar::chunk {{
        background-color: {colors.accent};
        border-radius: {RADIUS_SM}px;
    }}

    QListWidget {{
        background: {colors.input_bg};
        border: 1px solid {colors.border};
        border-radius: {RADIUS_MD}px;
        color: {colors.text};
        padding: 6px;
        outline: none;
    }}
    QListWidget::item {{
        padding: 6px 10px;
        border-radius: {RADIUS_SM}px;
    }}
    QListWidget::item:selected {{
        background: {colors.accent};
        color: white;
    }}

    QLineEdit, QSpinBox, QComboBox, QTextEdit {{
        background: {colors.input_bg};
        border: 1px solid {colors.border};
        border-radius: {RADIUS_SM}px;
        padding: 10px 14px;
        color: {colors.text};
        font-size: 13px;
    }}
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus {{
        border-color: {colors.accent};
    }}
    QSpinBox::up-button, QSpinBox::down-button {{
        background: {colors.border};
        border: none;
        width: 22px;
        border-radius: 4px;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}

    QGroupBox {{
        border: 1px solid {colors.border};
        border-radius: {RADIUS_MD}px;
        margin-top: 14px;
        padding-top: 14px;
        color: {colors.accent};
        font-size: 12px;
        font-weight: 700;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 14px;
        padding: 0 6px;
        background-color: {colors.bg};
    }}

    QCheckBox {{
        color: {colors.text};
        spacing: 10px;
        font-size: 13px;
    }}
    QCheckBox::indicator {{
        width: 20px; height: 20px;
        border: 2px solid {colors.border};
        border-radius: 5px;
        background: {colors.input_bg};
    }}
    QCheckBox::indicator:checked {{
        background: {colors.accent};
        border-color: {colors.accent};
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {colors.border};
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{ background: {colors.text_muted}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}

    QScrollBar:horizontal {{
        background: transparent;
        height: 8px;
    }}
    QScrollBar::handle:horizontal {{
        background: {colors.border};
        border-radius: 4px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}

    QToolTip {{
        background: {colors.panel};
        color: {colors.text};
        border: 1px solid {colors.border};
        border-radius: {RADIUS_SM}px;
        padding: 6px 10px;
        font-size: 12px;
    }}

    QMenu {{
        background: {colors.panel};
        border: 1px solid {colors.border};
        border-radius: {RADIUS_SM}px;
        padding: 6px;
    }}
    QMenu::item {{
        padding: 8px 24px;
        border-radius: 5px;
    }}
    QMenu::item:selected {{ background: {colors.accent}; }}

    QSlider::groove:horizontal {{
        background: {colors.progress_bg};
        height: 6px;
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: {colors.accent};
        width: 16px;
        height: 16px;
        margin: -5px 0;
        border-radius: 8px;
    }}
    QSlider::sub-page:horizontal {{
        background: {colors.accent};
        border-radius: 3px;
    }}
    """


def get_accent_palette() -> list:
    """Return a 4-color accent palette derived from current theme."""
    return [
        CURRENT.accent,
        CURRENT.accent_secondary,
        CURRENT.accent_tertiary,
        CURRENT.success,
    ]
