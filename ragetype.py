#!/usr/bin/env python3
"""
RageType — Your keyboard fights back.

Plays custom sound effects per key, with escalating intensity
based on how aggressively you type.

Sounds are loaded from:
  1. sounds/custom/  (user overrides, set via dashboard)
  2. sounds/default/ (ships with the app)

Expected filenames: a.mp3, b.mp3, ..., z.mp3, 0.mp3, 1.mp3, ..., 9.mp3
"""

import sys
import os
import time
import json
import math
import random
import struct
import threading
from collections import deque
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
    if missing:
        print(f"\n  Missing dependencies: {', '.join(missing)}")
        print(f"  Install with: python3 -m pip install {' '.join(missing)}\n")
        sys.exit(1)

check_deps()

from pynput import keyboard
from pygame import mixer

# ── Paths ─────────────────────────────────────────────────────────
APP_DIR = Path(__file__).parent.resolve()
DEFAULT_SOUNDS_DIR = APP_DIR / "sounds" / "default"
CUSTOM_SOUNDS_DIR = APP_DIR / "sounds" / "custom"
CONFIG_FILE = APP_DIR / "config.json"

# All supported keys
ALL_KEYS = [chr(c) for c in range(ord('a'), ord('z') + 1)] + [str(d) for d in range(10)]

# ── Rage levels ───────────────────────────────────────────────────
RAGE_LEVELS = [
    {"name": "Calm",         "threshold": 0,   "color": "\033[92m", "speed": 1.0},
    {"name": "Annoyed",      "threshold": 4,   "color": "\033[93m", "speed": 1.1},
    {"name": "Frustrated",   "threshold": 7,   "color": "\033[33m", "speed": 1.25},
    {"name": "Angry",        "threshold": 11,  "color": "\033[91m", "speed": 1.4},
    {"name": "RAGE",         "threshold": 16,  "color": "\033[31m", "speed": 1.6},
    {"name": "MELTDOWN",     "threshold": 22,  "color": "\033[35m", "speed": 2.0},
]

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"


# ── Config ────────────────────────────────────────────────────────
def load_config() -> dict:
    """Load key→sound mappings from config.json."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}

def save_config(config: dict):
    """Save key→sound mappings to config.json."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


# ── Sound loader ──────────────────────────────────────────────────
class SoundManager:
    def __init__(self):
        mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        # Allow many simultaneous sounds
        mixer.set_num_channels(32)
        self.sounds: dict[str, mixer.Sound] = {}
        self.config = load_config()
        self._load_all()

    def _load_all(self):
        """Load sound for each key. Priority: config override > custom dir > default dir."""
        loaded = 0
        missing = []

        for key in ALL_KEYS:
            sound_path = self._resolve_sound_path(key)
            if sound_path and sound_path.exists():
                try:
                    self.sounds[key] = mixer.Sound(str(sound_path))
                    loaded += 1
                except Exception as e:
                    missing.append(key)
            else:
                missing.append(key)

        print(f"  {DIM}Loaded {loaded}/{len(ALL_KEYS)} key sounds{RESET}")
        if missing:
            print(f"  {DIM}Missing sounds for: {', '.join(missing)}{RESET}")
            print(f"  {DIM}Place MP3 files in: {DEFAULT_SOUNDS_DIR}{RESET}")
            print(f"  {DIM}Expected format: a.mp3, b.mp3, ..., 0.mp3, 1.mp3, ...{RESET}")

    def _resolve_sound_path(self, key: str) -> Path | None:
        """Resolve which sound file to use for a key."""
        # 1. Check config override (absolute or relative path)
        if key in self.config:
            p = Path(self.config[key])
            if not p.is_absolute():
                p = APP_DIR / p
            if p.exists():
                return p

        # 2. Check custom sounds dir
        custom = CUSTOM_SOUNDS_DIR / f"{key}.mp3"
        if custom.exists():
            return custom

        # 3. Check default sounds dir
        default = DEFAULT_SOUNDS_DIR / f"{key}.mp3"
        if default.exists():
            return default

        return None

    def play(self, key: str, rage_level: int):
        """Play the sound for a key at the current rage intensity."""
        if key not in self.sounds:
            return

        sound = self.sounds[key]
        level_info = RAGE_LEVELS[min(rage_level, len(RAGE_LEVELS) - 1)]

        # Scale volume with rage (0.4 at calm → 1.0 at meltdown)
        volume = 0.4 + (rage_level / (len(RAGE_LEVELS) - 1)) * 0.6
        sound.set_volume(min(1.0, volume))

        # Find a free channel and play
        channel = mixer.find_channel(True)
        if channel:
            channel.play(sound)

    def reload(self):
        """Reload config and all sounds."""
        self.config = load_config()
        self.sounds.clear()
        self._load_all()


# ── Rage detector ─────────────────────────────────────────────────
class RageDetector:
    def __init__(self, sensitivity: float = 1.0):
        self.sensitivity = sensitivity
        self.keystroke_times: deque = deque(maxlen=100)
        self.total_keystrokes = 0
        self.peak_kps = 0.0
        self.rage_episodes = 0
        self.current_level = 0
        self.lock = threading.Lock()

    def record_keystroke(self) -> int:
        """Record a keystroke and return current rage level."""
        now = time.time()
        with self.lock:
            self.keystroke_times.append(now)
            self.total_keystrokes += 1

        kps = self._get_kps()
        if kps > self.peak_kps:
            self.peak_kps = kps

        new_level = self._calc_level(kps)
        if new_level >= 5 and self.current_level < 5:
            self.rage_episodes += 1
        self.current_level = new_level
        return new_level

    def _get_kps(self) -> float:
        now = time.time()
        with self.lock:
            while self.keystroke_times and now - self.keystroke_times[0] > 2.0:
                self.keystroke_times.popleft()
            if len(self.keystroke_times) < 2:
                return 0.0
            window = now - self.keystroke_times[0]
            return len(self.keystroke_times) / window if window > 0.01 else 0.0

    def _calc_level(self, kps: float) -> int:
        adjusted = kps * self.sensitivity
        level = 0
        for i, lvl in enumerate(RAGE_LEVELS):
            if adjusted >= lvl["threshold"]:
                level = i
        return level

    def get_display_data(self) -> dict:
        kps = self._get_kps()
        return {
            "kps": kps,
            "level": self.current_level,
            "total": self.total_keystrokes,
            "peak": self.peak_kps,
            "meltdowns": self.rage_episodes,
        }


# ── Main app ──────────────────────────────────────────────────────
class RageType:
    def __init__(self, sensitivity: float = 1.0, cooldown: float = 0.08):
        self.cooldown = cooldown
        self.sound_mgr = SoundManager()
        self.rage = RageDetector(sensitivity)
        self.last_sound_time = 0.0
        self.running = True

    def _key_to_name(self, key) -> str | None:
        """Convert pynput key to our key name (a-z, 0-9)."""
        try:
            char = key.char
            if char and char.lower() in ALL_KEYS:
                return char.lower()
        except AttributeError:
            pass
        return None

    def on_key_press(self, key):
        now = time.time()
        level = self.rage.record_keystroke()
        key_name = self._key_to_name(key)

        if key_name and now - self.last_sound_time >= self.cooldown:
            self.last_sound_time = now
            self.sound_mgr.play(key_name, level)

    def display_loop(self):
        while self.running:
            d = self.rage.get_display_data()
            lvl = RAGE_LEVELS[d["level"]]

            bar_w = 30
            fill = min(bar_w, int((d["kps"] / (RAGE_LEVELS[-1]["threshold"] + 5)) * bar_w))
            bar = "█" * fill + "░" * (bar_w - fill)

            line = (
                f"\r  {lvl['color']}{BOLD}{lvl['name']:^14}{RESET}"
                f"  {DIM}│{RESET} {lvl['color']}{bar}{RESET}"
                f"  {DIM}│{RESET} {d['kps']:5.1f} keys/s"
                f"  {DIM}│{RESET} total: {d['total']}"
                f"  {DIM}│{RESET} peak: {d['peak']:.1f}/s"
                f"  {DIM}│{RESET} meltdowns: {d['meltdowns']}"
                f"   "
            )
            sys.stdout.write(line)
            sys.stdout.flush()
            time.sleep(0.1)

    def run(self):
        os.system("cls" if os.name == "nt" else "clear")
        print()
        print(f"  {BOLD}╔══════════════════════════════════════════════════╗{RESET}")
        print(f"  {BOLD}║      ⌨️  RAGETYPE — Your keyboard fights back     ║{RESET}")
        print(f"  {BOLD}╚══════════════════════════════════════════════════╝{RESET}")
        print()
        self.sound_mgr  # triggers load log
        print()
        print(f"  {DIM}Type anywhere. The app listens globally.{RESET}")
        print(f"  {DIM}Dashboard: python3 dashboard.py  (then open http://localhost:8000){RESET}")
        print(f"  {DIM}Press Ctrl+C to quit{RESET}")
        print()

        t = threading.Thread(target=self.display_loop, daemon=True)
        t.start()

        with keyboard.Listener(on_press=self.on_key_press) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                self.running = False
                d = self.rage.get_display_data()
                print("\n")
                print(f"  {BOLD}Session stats:{RESET}")
                print(f"    Keystrokes:  {d['total']}")
                print(f"    Peak speed:  {d['peak']:.1f} keys/sec")
                print(f"    Meltdowns:   {d['meltdowns']}")
                print()


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="⌨️ RageType — Your keyboard fights back",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-s", "--sensitivity", type=float, default=1.0,
                        help="Sensitivity multiplier (default: 1.0)")
    parser.add_argument("-c", "--cooldown", type=float, default=0.08,
                        help="Min seconds between sounds (default: 0.08)")
    args = parser.parse_args()

    app = RageType(sensitivity=args.sensitivity, cooldown=args.cooldown)
    app.run()


if __name__ == "__main__":
    main()