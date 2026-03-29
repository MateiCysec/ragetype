# System Tray Mode

RageType can run silently in your system tray — no terminal window needed.

## Running in tray mode

```bash
python3 ragetype_tray.py
```

A keyboard icon will appear in your system tray (notification area on Windows, menu bar on macOS).

## Tray menu options

Right-click (or left-click on macOS) the tray icon to access:

| Option | Description |
|--------|-------------|
| **Pause / Resume** | Temporarily stop or resume sound playback |
| **Open Dashboard** | Launches the dashboard and opens your browser |
| **Reload Sounds** | Re-reads all sound files without restarting |
| **Sensitivity** | Adjust sensitivity (0.5x – 2.0x) |
| **Stats** | Shows current session stats (keystrokes, peak speed, meltdowns) |
| **Quit** | Stops RageType completely |

## Tray icon colors

The tray icon changes color based on your current rage level:

- 🟢 Teal = Calm
- 🟡 Yellow = Annoyed
- 🟠 Orange = Frustrated
- 🔴 Red = Angry / Rage
- 🟣 Purple = Meltdown

## Auto-start on boot

### Windows

1. Press `Win + R`, type `shell:startup`, press Enter
2. Create a shortcut to `python3 ragetype_tray.py` (or `RageType.exe` if you built it)
3. Place the shortcut in the startup folder

### Linux (systemd)

Create `~/.config/systemd/user/ragetype.service`:

```ini
[Unit]
Description=RageType

[Service]
ExecStart=/usr/bin/python3 /path/to/ragetype_tray.py
Restart=on-failure

[Install]
WantedBy=default.target
```

Then:
```bash
systemctl --user enable ragetype
systemctl --user start ragetype
```

### macOS

Create a Launch Agent at `~/Library/LaunchAgents/com.ragetype.plist` or use the `login items` system preference.