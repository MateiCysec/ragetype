# Security Policy

## Privacy & Data Handling

**RageType runs 100% locally on your machine.** Here's what that means:

- **No network calls.** RageType never connects to the internet. Zero telemetry, zero analytics, zero cloud.
- **No data leaves your computer.** Keystroke data is processed in-memory and never written to disk (except the optional lifetime stats counter in the terminal).
- **No keylogging.** RageType detects *typing speed* (keystrokes per second) and *which alphanumeric key* was pressed (to play the matching sound). It does not record what you type, does not store sequences, and does not capture passwords or sensitive input.
- **No background persistence.** When you close RageType, it stops. No background services, no startup entries (unless you add them yourself).
- **Local dashboard only.** The dashboard runs on `localhost:8000` and is only accessible from your machine. It is not exposed to your network.

## Permissions Explained

### Why does RageType need keyboard access?

RageType uses the `pynput` library to listen for global keypresses. This is necessary because:
- The app needs to detect typing speed *across all applications* (not just in its own window)
- It needs to know *which key* was pressed to play the correct sound file

On different platforms:
- **Windows**: No special permissions needed. `pynput` uses the Windows API.
- **macOS**: Requires Accessibility permission (System Preferences → Privacy & Security → Accessibility). This is a macOS requirement for any app that reads global keyboard input.
- **Linux**: May require running with `sudo` or adding your user to the `input` group (`sudo usermod -aG input $USER`).

### Why does the dashboard use a local web server?

The dashboard (`dashboard.py`) runs a simple HTTP server on `127.0.0.1:8000` (localhost only) to serve the management UI. This server:
- Only binds to `127.0.0.1` (not `0.0.0.0`) — it cannot be accessed from other devices on your network
- Only serves the dashboard page and handles sound file uploads
- Has no authentication because it's local-only — if you're concerned, don't run the dashboard

## Supported Versions

| Version | Supported |
|---------|-----------|
| latest  | ✅        |

## Reporting a Vulnerability

If you find a security issue, please **do not open a public issue**. Instead:

1. Email: [your-email@example.com]
2. Or use GitHub's [private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)

We'll respond within 48 hours and aim to patch confirmed vulnerabilities within 7 days.

## Security Best Practices

- **Download only from the official GitHub repository.** Do not trust third-party repackaged versions.
- **Verify checksums** if downloading pre-built executables from GitHub Releases.
- **Review the code.** It's open source and intentionally kept simple — the entire app is ~300 lines of Python.
- **Sound files are not executable.** RageType only loads `.mp3` files via pygame's audio decoder. Sound files cannot execute code.

## Dependency Security

RageType uses the following dependencies:
- `pynput` — keyboard input library (MIT license)
- `pygame` — audio playback (LGPL license)
- `pystray` — system tray integration (MIT license, tray mode only)
- `Pillow` — icon generation (MIT-like license, tray mode only)

All dependencies are pinned to minimum versions in `requirements.txt` and monitored via GitHub Dependabot.