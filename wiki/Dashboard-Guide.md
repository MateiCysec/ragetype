# Dashboard Guide

RageType includes a local web dashboard for managing sound assignments without touching the terminal.

## Starting the Dashboard

```bash
python3 dashboard.py
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

The dashboard runs locally on your machine — no internet connection needed, no data sent anywhere.

## Features

### Key overview

The main view shows all 36 keys in a grid. Each key is color-coded:

| Color | Meaning |
|-------|---------|
| Green | Default sound assigned |
| Purple | Custom sound uploaded |
| Yellow | Config override active |
| Gray | No sound (missing) |

### Preview sounds

Click any key to select it, then click **Play** to hear the current sound assignment.

### Upload custom sounds

1. Click a key to select it
2. Click **Upload MP3**
3. Select an MP3 file from your computer
4. The sound is saved to `sounds/custom/` and immediately assigned

### Reset to default

Click **Reset to default** to remove a custom sound and revert to the default.

### Stats bar

The top of the dashboard shows:
- **Total keys**: Always 36
- **Assigned**: How many keys have sounds
- **Custom**: How many use custom sounds
- **Missing**: How many keys have no sound at all

## Applying changes

After making changes in the dashboard, you need to restart `ragetype.py` (or `ragetype_tray.py`) for the new sounds to take effect. The tray version also has a "Reload Sounds" option in its menu.

## Security note

The dashboard server binds to `127.0.0.1` (localhost only). It cannot be accessed from other devices on your network. There is no authentication because it's local-only.