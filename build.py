#!/usr/bin/env python3
"""Build script untuk AntiDistract — PyInstaller wrapper.

Usage:
    python build.py              # one-folder build (default)
    python build.py --onefile    # single .exe build
    python build.py --clean      # clean build artifacts first
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
BUILD = ROOT / "build"
MODEL_DIR = Path.home() / ".antidistract" / "models"

NAME = "AntiDistract"
ENTRY = str(ROOT / "main.py")
ICON = str(ROOT / "assets" / "icons" / "logo.svg")

HIDDEN_IMPORTS = [
    "PyQt6",
    "PyQt6.QtCore",
    "PyQt6.QtGui",
    "PyQt6.QtWidgets",
    "cv2",
    "numpy",
    "pyqtgraph",
    "websockets",
    "queue",
    "json",
    "sqlite3",
    "datetime",
    "math",
    "random",
    "time",
    "urllib.request",
    "wave",
    "struct",
]

DATA_FILES = []


def collect_model_files():
    """Collect face detection model files for bundling."""
    models = []
    for fname in ["deploy.prototxt", "res10_300x300_ssd_iter_140000.caffemodel"]:
        src = MODEL_DIR / fname
        if src.exists():
            models.append((str(src), "models"))
    return models


def run(cmd: list[str], **kwargs):
    print(f"\n  {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(ROOT), **kwargs)
    if result.returncode != 0:
        print(f"\nBuild gagal (exit {result.returncode})")
        sys.exit(result.returncode)


def clean():
    for d in [DIST, BUILD]:
        if d.exists():
            print(f"  Membersihkan {d.name}/")
            shutil.rmtree(d)
    spec = ROOT / f"{NAME}.spec"
    if spec.exists():
        spec.unlink()


def build(onefile: bool = False, clean_first: bool = False):
    if clean_first:
        clean()

    data_args = []
    for src, dest in DATA_FILES:
        sep = ";" if sys.platform == "win32" else ":"
        data_args.extend(["--add-data", f"{src}{sep}{dest}"])

    model_data = collect_model_files()
    for src, dest in model_data:
        sep = ";" if sys.platform == "win32" else ":"
        data_args.extend(["--add-data", f"{src}{sep}{dest}"])

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", NAME,
        "--noconfirm",
        "--noconsole",
        "--clean",
    ]

    if ICON and Path(ICON).exists():
        cmd.extend(["--icon", ICON])

    if onefile:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")

    for mod in HIDDEN_IMPORTS:
        cmd.extend(["--hidden-import", mod])

    cmd.extend(data_args)
    cmd.append(ENTRY)

    print(f"\n{'='*60}")
    print(f"  AntiDistract Build")
    print(f"  Mode: {'onefile' if onefile else 'onedir'}")
    print(f"  Entry: {ENTRY}")
    print(f"  Model files: {len(model_data)} ditemukan")
    print(f"{'='*60}")

    run(cmd)

    # Done
    if onefile:
        exe = DIST / f"{NAME}.exe" if sys.platform == "win32" else DIST / NAME
    else:
        exe = DIST / NAME / (f"{NAME}.exe" if sys.platform == "win32" else NAME)

    if exe.exists():
        size_mb = exe.stat().st_size / (1024 * 1024)
        print(f"\n  Build berhasil: {exe} ({size_mb:.1f} MB)")
    else:
        print(f"\n  Build selesai, cek {DIST}/")
        for f in sorted(DIST.rglob("*")):
            if f.is_file():
                print(f"    {f.relative_to(DIST)}")


def main():
    parser = argparse.ArgumentParser(description="AntiDistract build script")
    parser.add_argument("--onefile", action="store_true", help="Single .exe build")
    parser.add_argument("--clean", action="store_true", help="Clean before build")
    args = parser.parse_args()

    if "--onefile" in sys.argv or "-h" in sys.argv or "--help" in sys.argv:
        pass

    try:
        import PyInstaller  # noqa
    except ImportError:
        print("PyInstaller belum terinstall.")
        print("  pip install pyinstaller")
        sys.exit(1)

    build(onefile=args.onefile, clean_first=args.clean)


if __name__ == "__main__":
    main()
