# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ragetype_tray.py'],
    pathex=[],
    binaries=[],
    datas=[('sounds/default', 'sounds/default'), ('sounds/custom', 'sounds/custom'), ('dashboard.py', '.')],
    hiddenimports=['pynput', 'pynput.keyboard', 'pynput.keyboard._win32', 'pynput.keyboard._xorg', 'pynput.keyboard._darwin', 'pygame', 'pygame.mixer', 'pystray', 'PIL'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='RageType',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
