"""
Daftarkan AntiDistract ke Windows Startup.
python setup_autostart.py install|remove|status
"""

import sys
from pathlib import Path

try:
    import winreg
except ImportError:
    print("Script ini hanya untuk Windows.")
    sys.exit(1)

APP_NAME = "AntiDistract"
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def find_pythonw() -> Path:
    python = Path(sys.executable)
    pythonw = python.parent / "pythonw.exe"
    return pythonw if pythonw.exists() else python


def get_main_script() -> Path:
    return Path(__file__).parent.parent / "main.py"


def build_command() -> str:
    pythonw = find_pythonw()
    main_py = get_main_script()
    return f'"{pythonw}" "{main_py}"'


def install():
    cmd = build_command()
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(key)
        print(f"AntiDistract akan otomatis jalan saat login Windows.")
        print(f"   Command: {cmd}")
    except Exception as e:
        print(f"Gagal: {e}")


def remove():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
        print("AntiDistract dihapus dari startup.")
    except FileNotFoundError:
        print("AntiDistract tidak ada di startup.")
    except Exception as e:
        print(f"Gagal: {e}")


def status():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        val, _ = winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        print(f"Terdaftar di startup: {val}")
    except FileNotFoundError:
        print("Belum terdaftar di startup.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("install", "remove", "status"):
        print(__doc__)
        sys.exit(0)

    action = sys.argv[1]
    {"install": install, "remove": remove, "status": status}[action]()
