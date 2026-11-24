# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

ROOT = Path(SPECPATH).resolve()

datas = [
    (str(ROOT / "launcher" / "assets" / "welcometour.ico"), "assets"),
    (str(ROOT / "launcher" / "assets" / "welcometour.png"), "assets"),
    (str(ROOT / "launcher" / "assets" / "welcometour_emblem.png"), "assets"),
    (str(ROOT / "launcher" / "welcometour_version.txt"), "."),
    (str(ROOT / "tools" / "data" / "expected-welcometour104.json"), "tools/data"),
    (str(ROOT / "tools" / "extract_nup.py"), "tools"),
]

a = Analysis(
    [str(ROOT / "launcher" / "WelcomeTourLauncher.py")],
    pathex=[str(ROOT / "launcher")],
    binaries=[],
    datas=datas,
    hiddenimports=["PIL._tkinter_finder", "welcometour_dump", "lz4", "lz4.block"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "unittest", "scipy", "matplotlib", "pandas"],
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
    name="WelcomeTourLauncher",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    icon=[str(ROOT / "launcher" / "assets" / "welcometour.ico")],
)
