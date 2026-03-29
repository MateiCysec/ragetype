#!/usr/bin/env python3
"""
RageType Dashboard — Local web UI for managing key→sound mappings.

Run:  python3 dashboard.py
Open: http://localhost:8000
"""

import json
import os
import shutil
import mimetypes
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs
import cgi
import io
import re

APP_DIR = Path(__file__).parent.resolve()
CONFIG_FILE = APP_DIR / "config.json"
CUSTOM_SOUNDS_DIR = APP_DIR / "sounds" / "custom"
DEFAULT_SOUNDS_DIR = APP_DIR / "sounds" / "default"
DASHBOARD_DIR = APP_DIR / "dashboard"

ALL_KEYS = [chr(c) for c in range(ord('a'), ord('z') + 1)] + [str(d) for d in range(10)]

def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}

def save_config(config: dict):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def get_key_status() -> list[dict]:
    """Get the current sound assignment status for every key."""
    config = load_config()
    result = []
    for key in ALL_KEYS:
        info = {"key": key, "source": "none", "file": None}

        # Check config override
        if key in config:
            p = Path(config[key])
            if not p.is_absolute():
                p = APP_DIR / p
            if p.exists():
                info["source"] = "custom (config)"
                info["file"] = config[key]
                result.append(info)
                continue

        # Check custom dir
        custom = CUSTOM_SOUNDS_DIR / f"{key}.mp3"
        if custom.exists():
            info["source"] = "custom"
            info["file"] = f"sounds/custom/{key}.mp3"
            result.append(info)
            continue

        # Check default dir
        default = DEFAULT_SOUNDS_DIR / f"{key}.mp3"
        if default.exists():
            info["source"] = "default"
            info["file"] = f"sounds/default/{key}.mp3"
            result.append(info)
            continue

        result.append(info)
    return result


class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self._serve_dashboard()
        elif self.path == "/api/keys":
            self._json_response(get_key_status())
        elif self.path.startswith("/api/sound/"):
            self._serve_sound()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path.startswith("/api/upload/"):
            self._handle_upload()
        elif self.path.startswith("/api/reset/"):
            self._handle_reset()
        else:
            self.send_error(404)

    def _json_response(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def _serve_sound(self):
        """Serve a sound file for preview playback."""
        key = self.path.split("/")[-1].lower()
        if key not in ALL_KEYS:
            self.send_error(404)
            return

        # Find the sound file
        config = load_config()
        sound_path = None
        if key in config:
            p = Path(config[key])
            if not p.is_absolute():
                p = APP_DIR / p
            if p.exists():
                sound_path = p
        if not sound_path:
            for d in [CUSTOM_SOUNDS_DIR, DEFAULT_SOUNDS_DIR]:
                p = d / f"{key}.mp3"
                if p.exists():
                    sound_path = p
                    break

        if not sound_path:
            self.send_error(404)
            return

        data = sound_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "audio/mpeg")
        self.send_header("Content-Length", len(data))
        self.end_headers()
        self.wfile.write(data)

    def _handle_upload(self):
        """Handle MP3 upload for a specific key."""
        key = self.path.split("/")[-1].lower()
        if key not in ALL_KEYS:
            self._json_response({"error": "Invalid key"}, 400)
            return

        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            self._json_response({"error": "Expected multipart/form-data"}, 400)
            return

        # Parse multipart
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        boundary = content_type.split("boundary=")[-1].strip()
        parts = body.split(f"--{boundary}".encode())

        file_data = None
        for part in parts:
            if b"filename=" in part:
                # Extract file data after the double newline
                header_end = part.find(b"\r\n\r\n")
                if header_end != -1:
                    file_data = part[header_end + 4:]
                    # Remove trailing \r\n
                    if file_data.endswith(b"\r\n"):
                        file_data = file_data[:-2]
                    break

        if not file_data:
            self._json_response({"error": "No file data received"}, 400)
            return

        # Save to custom sounds dir
        CUSTOM_SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
        dest = CUSTOM_SOUNDS_DIR / f"{key}.mp3"
        dest.write_bytes(file_data)

        self._json_response({"status": "ok", "key": key, "file": str(dest)})

    def _handle_reset(self):
        """Reset a key back to default sound."""
        key = self.path.split("/")[-1].lower()
        if key not in ALL_KEYS:
            self._json_response({"error": "Invalid key"}, 400)
            return

        # Remove custom file
        custom = CUSTOM_SOUNDS_DIR / f"{key}.mp3"
        if custom.exists():
            custom.unlink()

        # Remove config override
        config = load_config()
        if key in config:
            del config[key]
            save_config(config)

        self._json_response({"status": "ok", "key": key})

    def _serve_dashboard(self):
        html = DASHBOARD_HTML.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(html))
        self.end_headers()
        self.wfile.write(html)

    def log_message(self, format, *args):
        # Quieter logs
        pass


# ── Dashboard HTML (single-file, no external deps) ───────────────
DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RageType Dashboard</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Instrument+Serif:ital@0;1&display=swap');

  :root {
    --bg: #0a0a0a;
    --surface: #111;
    --border: #1e1e1e;
    --text: #e8e0d8;
    --dim: #555;
    --red: #ff2d2d;
    --green: #4ecdc4;
    --yellow: #ffd23f;
    --orange: #ff6b35;
    --purple: #c77dff;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Space Mono', monospace;
    padding: 2rem;
    max-width: 1100px;
    margin: 0 auto;
  }

  header {
    margin-bottom: 3rem;
    border-bottom: 1px solid var(--border);
    padding-bottom: 2rem;
  }

  header h1 {
    font-family: 'Instrument Serif', serif;
    font-size: 2.5rem;
    font-weight: 400;
    margin-bottom: 0.5rem;
  }

  header h1 span { color: var(--red); font-style: italic; }

  header p {
    font-size: 0.8rem;
    color: var(--dim);
    line-height: 1.6;
  }

  .stats-bar {
    display: flex;
    gap: 2rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
  }

  .stat {
    font-size: 0.75rem;
    color: var(--dim);
  }

  .stat strong {
    color: var(--text);
    font-size: 1.2rem;
    display: block;
    margin-top: 0.25rem;
  }

  .stat strong.all-good { color: var(--green); }
  .stat strong.has-missing { color: var(--orange); }

  /* ── Keyboard grid ── */
  .section-label {
    font-size: 0.65rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--dim);
    margin-bottom: 1.5rem;
    margin-top: 2rem;
  }

  .key-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(70px, 1fr));
    gap: 8px;
    margin-bottom: 2rem;
  }

  .key-card {
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 0.8rem 0.5rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.15s;
    position: relative;
  }

  .key-card:hover {
    border-color: #444;
    transform: translateY(-2px);
  }

  .key-card.selected {
    border-color: var(--red);
    box-shadow: 0 0 20px rgba(255,45,45,0.1);
  }

  .key-label {
    font-size: 1.2rem;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
  }

  .key-status {
    font-size: 0.55rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }

  .key-card[data-source="default"] .key-status { color: var(--green); }
  .key-card[data-source="custom"] .key-status { color: var(--purple); }
  .key-card[data-source="custom (config)"] .key-status { color: var(--yellow); }
  .key-card[data-source="none"] .key-status { color: var(--dim); }
  .key-card[data-source="none"] { opacity: 0.5; }

  /* ── Detail panel ── */
  .detail-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 2rem;
    margin-top: 1rem;
    display: none;
  }

  .detail-panel.visible { display: block; }

  .detail-header {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .detail-key {
    font-size: 2.5rem;
    font-weight: 700;
    text-transform: uppercase;
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid var(--border);
    flex-shrink: 0;
  }

  .detail-info h3 { font-size: 0.85rem; margin-bottom: 0.3rem; }
  .detail-info p { font-size: 0.7rem; color: var(--dim); }

  .detail-actions {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    align-items: center;
  }

  .btn {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    padding: 0.7em 1.5em;
    border: none;
    cursor: pointer;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    transition: transform 0.1s;
  }

  .btn:hover { transform: scale(1.03); }
  .btn:active { transform: scale(0.97); }

  .btn-play {
    background: var(--green);
    color: var(--bg);
    font-weight: 700;
  }

  .btn-upload {
    background: var(--red);
    color: var(--bg);
    font-weight: 700;
  }

  .btn-reset {
    background: transparent;
    color: var(--dim);
    border: 1px solid var(--border);
  }

  .btn-reset:hover { border-color: var(--dim); }

  #file-input { display: none; }

  .upload-status {
    font-size: 0.7rem;
    color: var(--dim);
    margin-top: 0.75rem;
    min-height: 1.2em;
  }

  .upload-status.success { color: var(--green); }
  .upload-status.error { color: var(--red); }

  /* ── Footer ── */
  footer {
    margin-top: 4rem;
    padding-top: 2rem;
    border-top: 1px solid var(--border);
    font-size: 0.65rem;
    color: #333;
  }

  footer a { color: var(--dim); text-decoration: none; }
</style>
</head>
<body>

<header>
  <h1><span>Rage</span>Type Dashboard</h1>
  <p>Manage sound assignments for each key. Upload custom MP3s or use the defaults.<br>
     Changes take effect next time you restart ragetype.py (or it auto-reloads).</p>
</header>

<div class="stats-bar">
  <div class="stat">Total keys<strong id="stat-total">36</strong></div>
  <div class="stat">Assigned<strong id="stat-assigned">—</strong></div>
  <div class="stat">Custom<strong id="stat-custom">—</strong></div>
  <div class="stat">Missing<strong id="stat-missing">—</strong></div>
</div>

<div class="section-label">Letters</div>
<div class="key-grid" id="letters-grid"></div>

<div class="section-label">Digits</div>
<div class="key-grid" id="digits-grid"></div>

<div class="detail-panel" id="detail-panel">
  <div class="detail-header">
    <div class="detail-key" id="detail-key-label">A</div>
    <div class="detail-info">
      <h3 id="detail-title">Key: A</h3>
      <p id="detail-source">Source: default — sounds/default/a.mp3</p>
    </div>
  </div>
  <div class="detail-actions">
    <button class="btn btn-play" id="btn-play" onclick="playSound()">▶ Play</button>
    <button class="btn btn-upload" onclick="document.getElementById('file-input').click()">Upload MP3</button>
    <button class="btn btn-reset" id="btn-reset" onclick="resetKey()">Reset to default</button>
    <input type="file" id="file-input" accept=".mp3,audio/mpeg" onchange="uploadFile(event)">
  </div>
  <div class="upload-status" id="upload-status"></div>
</div>

<footer>
  <p>RageType &copy; 2026 &nbsp;·&nbsp; <a href="/">Home</a> &nbsp;·&nbsp; Dashboard runs on localhost:8000</p>
</footer>

<script>
  let keys = [];
  let selectedKey = null;
  let currentAudio = null;

  async function loadKeys() {
    const res = await fetch('/api/keys');
    keys = await res.json();
    render();
  }

  function render() {
    const lettersGrid = document.getElementById('letters-grid');
    const digitsGrid = document.getElementById('digits-grid');
    lettersGrid.innerHTML = '';
    digitsGrid.innerHTML = '';

    let assigned = 0, custom = 0, missing = 0;

    keys.forEach(k => {
      const card = document.createElement('div');
      card.className = 'key-card' + (selectedKey === k.key ? ' selected' : '');
      card.dataset.source = k.source;
      card.onclick = () => selectKey(k.key);

      const label = document.createElement('div');
      label.className = 'key-label';
      label.textContent = k.key.toUpperCase();

      const status = document.createElement('div');
      status.className = 'key-status';
      status.textContent = k.source === 'none' ? 'missing' : k.source;

      card.appendChild(label);
      card.appendChild(status);

      if (k.key.match(/[a-z]/)) lettersGrid.appendChild(card);
      else digitsGrid.appendChild(card);

      if (k.source !== 'none') assigned++;
      if (k.source.includes('custom')) custom++;
      if (k.source === 'none') missing++;
    });

    const assignedEl = document.getElementById('stat-assigned');
    assignedEl.textContent = assigned + '/36';
    assignedEl.className = assigned === 36 ? 'all-good' : 'has-missing';

    document.getElementById('stat-custom').textContent = custom;

    const missingEl = document.getElementById('stat-missing');
    missingEl.textContent = missing;
    missingEl.className = missing === 0 ? 'all-good' : 'has-missing';
  }

  function selectKey(key) {
    selectedKey = key;
    const k = keys.find(x => x.key === key);
    if (!k) return;

    document.getElementById('detail-key-label').textContent = key.toUpperCase();
    document.getElementById('detail-title').textContent = 'Key: ' + key.toUpperCase();
    document.getElementById('detail-source').textContent =
      k.source === 'none'
        ? 'No sound assigned. Upload an MP3 or place ' + key + '.mp3 in sounds/default/'
        : 'Source: ' + k.source + (k.file ? ' — ' + k.file : '');

    document.getElementById('btn-play').disabled = k.source === 'none';
    document.getElementById('btn-reset').style.display =
      k.source.includes('custom') ? '' : 'none';

    document.getElementById('detail-panel').classList.add('visible');
    document.getElementById('upload-status').textContent = '';
    render();
  }

  function playSound() {
    if (!selectedKey) return;
    if (currentAudio) { currentAudio.pause(); currentAudio = null; }
    currentAudio = new Audio('/api/sound/' + selectedKey + '?t=' + Date.now());
    currentAudio.play().catch(() => {});
  }

  async function uploadFile(event) {
    const file = event.target.files[0];
    if (!file || !selectedKey) return;

    const statusEl = document.getElementById('upload-status');
    statusEl.textContent = 'Uploading...';
    statusEl.className = 'upload-status';

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/upload/' + selectedKey, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (res.ok) {
        statusEl.textContent = 'Uploaded! Sound assigned to ' + selectedKey.toUpperCase();
        statusEl.className = 'upload-status success';
        await loadKeys();
        selectKey(selectedKey);
      } else {
        statusEl.textContent = 'Error: ' + (data.error || 'Upload failed');
        statusEl.className = 'upload-status error';
      }
    } catch (e) {
      statusEl.textContent = 'Error: ' + e.message;
      statusEl.className = 'upload-status error';
    }

    event.target.value = '';
  }

  async function resetKey() {
    if (!selectedKey) return;
    await fetch('/api/reset/' + selectedKey, { method: 'POST' });
    await loadKeys();
    selectKey(selectedKey);
    document.getElementById('upload-status').textContent = 'Reset to default.';
    document.getElementById('upload-status').className = 'upload-status success';
  }

  loadKeys();
</script>
</body>
</html>
"""


def main():
    port = 8000
    server = HTTPServer(("127.0.0.1", port), DashboardHandler)
    print(f"\n  ⌨️  RageType Dashboard")
    print(f"  Open http://localhost:{port} in your browser")
    print(f"  Press Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Dashboard stopped.")
        server.server_close()


if __name__ == "__main__":
    main()