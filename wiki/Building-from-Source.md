# Building from Source

Create a standalone executable that users can run without installing Python.

## Prerequisites

```bash
python3 -m pip install pyinstaller
```

## Building

### Tray version (recommended)

```bash
python3 build.py
```

Creates `dist/RageType.exe` (Windows) or `dist/RageType` (Linux/macOS). This is the windowed tray version with no console window.

### Terminal version

```bash
python3 build.py --cli
```

Creates the same executable but with a terminal window for the rage meter display.

## What gets bundled

The build script bundles:
- All Python code
- `sounds/default/` directory (your default sound pack)
- `sounds/custom/` directory
- `dashboard.py` (for the "Open Dashboard" tray option)

## Distributing

### Option 1: Single .exe

The `--onefile` build creates a single executable. Users just download and run it. Sound files are extracted to a temp directory at runtime.

### Option 2: Zip package

For better performance (no temp extraction on each launch):

```bash
# After building:
mkdir RageType-v1.0
cp dist/RageType.exe RageType-v1.0/
cp -r sounds/ RageType-v1.0/
cp dashboard.py RageType-v1.0/
zip -r RageType-v1.0-windows.zip RageType-v1.0/
```

## GitHub Releases

The CI workflow (`.github/workflows/ci.yml`) automatically builds a Windows executable on every push to `main`. You can download it from the Actions tab, or create a GitHub Release to make it publicly available.

## Troubleshooting

### Windows Defender / SmartScreen warning

PyInstaller executables are not code-signed, so Windows may show a warning. Users can click "More info" → "Run anyway". To avoid this, you can sign the executable with a code signing certificate.

### Missing DLLs on Windows

If the executable fails with missing DLL errors, try:

```bash
python3 -m pip install pyinstaller --upgrade
python3 build.py
```

### Large file size

The executable includes Python itself plus all dependencies. Typical size is 30-50MB. To reduce size, you can use UPX compression (add `--upx-dir /path/to/upx` to the PyInstaller command in `build.py`)