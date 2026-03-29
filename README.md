# ⌨️ RageType

**Your keyboard fights back.**

RageType plays a unique sound for every key you press — and as you type faster, the rage escalates through 6 levels of audio chaos. Comes with default sounds for all 26 letters and 10 digits, plus a local dashboard to upload your own.

> Inspired by [SlapMac](https://slapmymac.com) — but for **every platform**, and triggered by your actual typing fury.

---

## How it works

1. **Every key has its own sound** — `a.mp3`, `b.mp3`, ..., `0.mp3`, `1.mp3`, etc.
2. **Rage detection** — RageType tracks your keystrokes per second in real-time
3. **Escalation** — Volume and intensity scale with how fast you're typing
4. **6 rage levels** — From 😌 Calm to ☢️ MELTDOWN

| Level | Trigger | What happens |
|-------|---------|-------------|
| 😌 Calm | Normal typing | Quiet key sounds |
| 😤 Annoyed | ~4 keys/sec | Volume starts rising |
| 😠 Frustrated | ~7 keys/sec | Getting loud |
| 🤬 Angry | ~11 keys/sec | Full volume |
| 💢 RAGE | ~16 keys/sec | Maximum intensity |
| ☢️ MELTDOWN | ~22 keys/sec | Nuclear |

## Quick start

```bash
# Clone
git clone https://github.com/MateiCysec/ragetype.git
cd ragetype

# Install dependencies
python3 -m pip install -r requirements.txt

# Place your sound files (a.mp3 through z.mp3, 0.mp3 through 9.mp3)
# into sounds/default/

# Run
python3 ragetype.py
```

### Options

```bash
python3 ragetype.py -s 1.5     # More sensitive (triggers easier)
python3 ragetype.py -s 0.7     # Less sensitive (for fast typers)
python3 ragetype.py -c 0.05    # Shorter cooldown between sounds
```

## Dashboard

RageType includes a local web dashboard to manage your sound assignments:

```bash
python3 dashboard.py
# Open http://localhost:8000
```

From the dashboard you can:
- **See** which keys have sounds assigned (and which are missing)
- **Preview** any key's current sound
- **Upload** custom MP3s for any key
- **Reset** a key back to its default sound

<details>
<summary>📸 Dashboard screenshot</summary>

_Screenshot placeholder — add after first run_

</details>

## Project structure

```
ragetype/
├── ragetype.py          # Main app — keyboard listener + sound player
├── dashboard.py         # Local web dashboard (http://localhost:8000)
├── config.json          # Auto-generated — stores custom key mappings
├── requirements.txt     # Python dependencies
├── sounds/
│   ├── default/         # Ships with the app (a.mp3 ... z.mp3, 0.mp3 ... 9.mp3)
│   └── custom/          # Your uploads override defaults (same naming)
├── docs/                # GitHub Pages landing page
│   └── index.html
├── .gitignore
├── LICENSE
└── README.md
```

### Sound resolution order

For each key, RageType checks in this order:
1. **config.json** override (set via dashboard)
2. **sounds/custom/** directory
3. **sounds/default/** directory

## Platform support

| Platform | Status | Notes |
|----------|--------|-------|
| Windows 10/11 | ✅ | Works out of the box |
| Linux (X11) | ✅ | May need `sudo` or `input` group |
| Linux (Wayland) | ⚠️ | Works with XWayland |
| macOS | ✅ | Needs Accessibility permission |

### Linux setup

```bash
# Add yourself to the input group (avoids needing sudo)
sudo usermod -aG input $USER
# Log out and back in for the change to take effect
```

## Creating sound packs

A sound pack is just a folder with 36 MP3 files:

```
my-sound-pack/
├── a.mp3
├── b.mp3
├── ...
├── z.mp3
├── 0.mp3
├── 1.mp3
├── ...
└── 9.mp3
```

To use a sound pack, copy the files into `sounds/default/` (or `sounds/custom/` to override).

**Sound pack ideas:**
- 🎹 Piano notes (each key = different note)
- 🐱 Cat meows (pitched differently per key)
- 👊 Fighting game hits
- 🎮 Retro game bleeps
- 🥁 Drum kit
- 🗣️ Voice clips

## Contributing

PRs welcome! Some ideas:

- [ ] Sound pack marketplace / sharing
- [ ] System tray GUI (no terminal needed)
- [ ] Per-key volume control in dashboard
- [ ] Rage level sound overlays (extra sounds at high rage)
- [ ] Rage stats history / leaderboard
- [ ] Auto-reload when dashboard changes sounds

## License

MIT — Do whatever you want. Ship it. Make money. Rage on.