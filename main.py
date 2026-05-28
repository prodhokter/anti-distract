import sys
from ui.app import setup_app
from core.database import init_db
from network.ws_server import WSServer
from ui.main_window import MainWindow

def main():
    init_db()       # ← init DB dulu
    app = setup_app()
    ws = WSServer()
    ws.start()
    window = MainWindow(ws_server=ws)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()