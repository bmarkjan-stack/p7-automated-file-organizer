# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for the Automated File Organizer.
#
# Build from the project root with:
#   pyinstaller build_scripts/organizer.spec --distpath dist --workpath build_scripts/work --noconfirm
#
# (build_exe.bat / build_exe.sh do exactly this for you.)

from pathlib import Path

# This file's own folder, so paths resolve the same way regardless of the
# working directory PyInstaller is invoked from.
SPEC_DIR = Path(SPECPATH)
PROJECT_ROOT = SPEC_DIR.parent

block_cipher = None

a = Analysis(
    [str(PROJECT_ROOT / "main.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=[],
    hiddenimports=[
        # tkinter's submodules are occasionally missed by PyInstaller's
        # static analysis depending on platform/version; listing them
        # explicitly avoids a "no module named tkinter.X" surprise at
        # runtime in the packaged .exe.
        "tkinter",
        "tkinter.filedialog",
        "tkinter.messagebox",
        "tkinter.scrolledtext",
        "tkinter.ttk",
    ],
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
    name="FileOrganizer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    # console=False -> no black terminal window pops up; the GUI is the
    # whole experience. Switch to True temporarily if you need to see
    # print()/traceback output while debugging a packaged build.
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(PROJECT_ROOT / "assets" / "icon.ico"),
)
