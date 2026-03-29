#!/usr/bin/env python3
"""
Build RageType into a standalone executable.

Usage:
    python3 build.py          # Build the tray version (recommended)
    python3 build.py --cli    # Build the terminal version

Requirements:
    python3 -m pip install pyinstaller

Output:
    dist/RageType.exe  (Windows)
    dist/RageType      (Linux/macOS)
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

APP_DIR = Path(__file__).parent.resolve()


def check_pyinstaller():
    try:
        import PyInstaller
        return True
    except ImportError:
        print("\n  PyInstaller not found.")
        print("  Install with: python3 -m pip install pyinstaller\n")
        return False


def build(cli_mode: bool = False):
    if not check_pyinstaller():
        sys.exit(1)

    entry = "ragetype.py" if cli_mode else "ragetype_tray.py"
    name = "RageType"
    icon_path = APP_DIR / "assets" / "icon.ico"

    print(f"\n  Building {name} ({'CLI' if cli_mode else 'Tray'} mode)...")
    print(f"  Entry point: {entry}\n")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", name,
        "--onefile",
        # Include sound directories as data
        "--add-data", f"sounds/default{os.pathsep}sounds/default",
        "--add-data", f"sounds/custom{os.pathsep}sounds/custom",
        "--add-data", f"dashboard.py{os.pathsep}.",
        # Hidden imports that PyInstaller might miss
        "--hidden-import", "pynput",
        "--hidden-import", "pynput.keyboard",
        "--hidden-import", "pynput.keyboard._win32",
        "--hidden-import", "pynput.keyboard._xorg",
        "--hidden-import", "pynput.keyboard._darwin",
        "--hidden-import", "pygame",
        "--hidden-import", "pygame.mixer",
        # Clean build
        "--clean",
        "--noconfirm",
    ]

    if not cli_mode:
        # Tray mode: no console window
        cmd.append("--windowed")
        cmd.extend(["--hidden-import", "pystray"])
        cmd.extend(["--hidden-import", "PIL"])

    # Add icon if it exists
    if icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])

    cmd.append(entry)

    print(f"  Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=str(APP_DIR))

    if result.returncode == 0:
        dist_dir = APP_DIR / "dist"
        print(f"\n  ✅ Build successful!")
        print(f"  Output: {dist_dir / name}{'.exe' if os.name == 'nt' else ''}")
        print(f"\n  To distribute, zip the executable together with the sounds/ folder.")
        print(f"  Or the sounds will be bundled inside the .exe automatically.\n")
    else:
        print(f"\n  ❌ Build failed with exit code {result.returncode}\n")
        sys.exit(1)


def main():
    cli_mode = "--cli" in sys.argv
    build(cli_mode)


if __name__ == "__main__":
    main()