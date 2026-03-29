# Installation

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Step-by-step

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ragetype.git
cd ragetype
```

### 2. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

This installs: `pynput` (keyboard listener), `pygame` (audio playback), `pystray` (system tray), `Pillow` (icon generation).

### 3. Add your sounds

Place 36 MP3 files in the `sounds/default/` directory:

```
sounds/default/
├── a.mp3
├── b.mp3
├── ...
├── z.mp3
├── 0.mp3
├── 1.mp3
├── ...
└── 9.mp3
```

Each file should be a short audio clip (under 1 second is ideal, under 100KB per file).

### 4. Run it

**Terminal mode:**
```bash
python3 ragetype.py
```

**System tray mode (no terminal):**
```bash
python3 ragetype_tray.py
```

## Platform-specific notes

### Windows
- Works out of the box. No special permissions needed.
- If `python3` isn't recognized, try `python` instead.
- Use `python -m pip` instead of `pip` if pip isn't on your PATH.

### Linux
- You may need keyboard access permissions:
  ```bash
  sudo usermod -aG input $USER
  ```
  Then log out and back in.
- Audio requires ALSA or PulseAudio. Install `libasound2-dev` if pygame can't find audio:
  ```bash
  sudo apt-get install libasound2-dev
  ```

### macOS
- Requires Accessibility permission: System Preferences → Privacy & Security → Accessibility → enable your terminal or Python.
- First run may show a permission dialog — click "Allow".

## Verifying the installation

```bash
python3 -c "import pynput, pygame; print('All good!')"
```

If this prints "All good!" you're ready to go.