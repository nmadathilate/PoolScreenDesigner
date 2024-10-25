# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['DrawingApp.py'],
    pathex=[],
    binaries=[],
    datas=[('Bar.py', '.'), ('DrawingSection.py', '.')],
    hiddenimports=['Bar', 'PyQt6.QtWidgets', 'PyQt6.QtGui', 'PyQt6.QtCore'],
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
    name='DrawingApp',
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

app = BUNDLE(
    exe,
    name='DrawingApp.app',

    bundle_identifier=None,
)
