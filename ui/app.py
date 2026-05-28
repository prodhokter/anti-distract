from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
import sys

from core.database import init_db
from core.repositories.settings_repo import get_setting
from config.theme import build_stylesheet, DARK, LIGHT, set_theme


def setup_app() -> QApplication:
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("AntiDistract")
    app.setOrganizationName("prodhokter")
    app.setQuitOnLastWindowClosed(False)

    is_dark = get_setting("theme", "light") == "dark"
    set_theme(is_dark)
    theme = DARK if is_dark else LIGHT
    app.setStyleSheet(build_stylesheet(theme))
    return app
