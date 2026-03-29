#!/usr/bin/env python3
"""
RageType Tray — System tray version.

Runs RageType silently in the system tray with a menu for:
  - Pause / Resume
  - Open Dashboard
  - Adjust sensitivity
  - View session stats
  - Quit

Works on Windows, macOS, and Linux.
"""

import sys
import os
import time
import threading
import webbrowser
import subprocess
from pathlib import Path

# ── Dependency check ──────────────────────────────────────────────
def check_deps():
    missing = []
    try:
        import pynput
    except ImportError:
        missing.append("pynput")
    try:
        from pygame import mixer
    except ImportError:
        missing.append("pygame")
    try:
        import pystray
    except ImportError:
        missing.append("pystray")
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        missing.append("Pillow")
    if missing:
        print(f"\n  Missing dependencies: {', '.join(missing)}")
        print(f"  Install with: python3 -m pip install {' '.join(missing)}\n")
        sys.exit(1)

check_deps()

import pystray
from PIL import Image, ImageDraw, ImageFont
from pynput import keyboard

# Import core modules from ragetype.py
APP_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(APP_DIR))
from ragetype import RageType, SoundManager, RageDetector, ALL_KEYS, RAGE_LEVELS


# ── Tray icon generator ──────────────────────────────────────────
def create_icon_image(rage_level: int = 0) -> Image.Image:
    """Generate a tray icon that changes color with rage level."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    colors = [
        (78, 205, 196),    # calm - teal
        (255, 210, 63),    # annoyed - yellow
        (255, 107, 53),    # frustrated - orange
        (255, 68, 68),     # angry - red
        (255, 45, 45),     # rage - bright red
        (199, 125, 255),   # meltdown - purple
    ]
    color = colors[min(rage_level, len(colors) - 1)]

    # Draw a keyboard-like icon
    pad = 6
    # Outer rounded rect (keyboard body)
    draw.rounded_rectangle(
        [pad, pad + 8, size - pad, size - pad],
        radius=6,
        fill=color,
    )

    # Key rows (3 rows of small squares)
    key_color = (10, 10, 10)
    rows = [
        (3, 16),  # row y-offset, num keys
        (3, 26),
        (3, 36),
    ]
    for num_keys_extra, row_y in rows:
        for i in range(4):
            kx = pad + 5 + i * 12
            ky = pad + row_y
            draw.rounded_rectangle(
                [kx, ky, kx + 9, ky + 8],
                radius=2,
                fill=key_color,
            )

    # Rage indicator dots at top
    if rage_level > 0:
        for i in range(min(rage_level, 5)):
            cx = 14 + i * 9
            draw.ellipse([cx, 2, cx + 5, 7], fill=color)

    return img


# ── Tray application ─────────────────────────────────────────────
class RageTypeTray:
    def __init__(self):
        self.sensitivity = 1.0
        self.cooldown = 0.08
        self.paused = False
        self.running = True
        self.sound_mgr = None
        self.rage = None
        self.last_sound_time = 0.0
        self.listener = None
        self.icon = None
        self.dashboard_process = None

    def _init_audio(self):
        """Initialize audio on a background thread."""
        self.sound_mgr = SoundManager()
        self.rage = RageDetector(self.sensitivity)

    def _key_to_name(self, key) -> str | None:
        try:
            char = key.char
            if char and char.lower() in ALL_KEYS:
                return char.lower()
        except AttributeError:
            pass
        return None

    def on_key_press(self, key):
        if self.paused or not self.sound_mgr or not self.rage:
            return
        now = time.time()
        level = self.rage.record_keystroke()
        key_name = self._key_to_name(key)

        if key_name and now - self.last_sound_time >= self.cooldown:
            self.last_sound_time = now
            self.sound_mgr.play(key_name, level)

        # Update tray icon color periodically
        if self.icon and self.rage.total_keystrokes % 20 == 0:
            try:
                self.icon.icon = create_icon_image(level)
            except Exception:
                pass

    def toggle_pause(self, icon, item):
        self.paused = not self.paused
        self._update_menu()

    def open_dashboard(self, icon, item):
        """Launch dashboard.py and open browser."""
        dashboard_path = APP_DIR / "dashboard.py"
        if not dashboard_path.exists():
            return

        if self.dashboard_process is None or self.dashboard_process.poll() is not None:
            creation_flags = 0
            if os.name == "nt":
                creation_flags = subprocess.CREATE_NO_WINDOW
            self.dashboard_process = subprocess.Popen(
                [sys.executable, str(dashboard_path)],
                creationflags=creation_flags if os.name == "nt" else 0,
            )
            time.sleep(1)

        webbrowser.open("http://localhost:8000")

    def reload_sounds(self, icon, item):
        if self.sound_mgr:
            self.sound_mgr.reload()

    def set_sensitivity(self, value):
        def handler(icon, item):
            self.sensitivity = value
            if self.rage:
                self.rage.sensitivity = value
            self._update_menu()
        return handler

    def get_stats_text(self) -> str:
        if not self.rage:
            return "No data yet"
        d = self.rage.get_display_data()
        return (
            f"Keys: {d['total']} | "
            f"Peak: {d['peak']:.1f}/s | "
            f"Meltdowns: {d['meltdowns']}"
        )

    def quit_app(self, icon, item):
        self.running = False
        if self.listener:
            self.listener.stop()
        if self.dashboard_process and self.dashboard_process.poll() is None:
            self.dashboard_process.terminate()
        icon.stop()

    def _build_menu(self):
        sens_values = [0.5, 0.7, 1.0, 1.3, 1.5, 2.0]
        return pystray.Menu(
            pystray.MenuItem(
                "Pause" if not self.paused else "Resume",
                self.toggle_pause,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Open Dashboard", self.open_dashboard),
            pystray.MenuItem("Reload Sounds", self.reload_sounds),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Sensitivity",
                pystray.Menu(
                    *[
                        pystray.MenuItem(
                            f"{'> ' if self.sensitivity == v else '  '}{v}x",
                            self.set_sensitivity(v),
                        )
                        for v in sens_values
                    ]
                ),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                lambda item: self.get_stats_text(),
                None,
                enabled=False,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self.quit_app),
        )

    def _update_menu(self):
        if self.icon:
            self.icon.menu = self._build_menu()
            self.icon.update_menu()

    def run(self):
        """Start the tray application."""
        # Init audio in background
        init_thread = threading.Thread(target=self._init_audio, daemon=True)
        init_thread.start()

        # Start keyboard listener
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

        # Wait for audio init
        init_thread.join(timeout=5)

        # Create and run tray icon
        self.icon = pystray.Icon(
            name="RageType",
            icon=create_icon_image(0),
            title="RageType — Your keyboard fights back",
            menu=self._build_menu(),
        )

        self.icon.run()


def main():
    app = RageTypeTray()
    app.run()


if __name__ == "__main__":
    main()