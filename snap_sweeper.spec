# -*- mode: python ; coding: utf-8 -*-
import os

from PyInstaller.utils.hooks import collect_all

libsvm_datas, libsvm_binaries, libsvm_hiddenimports = collect_all("libsvm")
chromadb_datas, chromadb_binaries, chromadb_hiddenimports = collect_all("chromadb")
brisque_datas, brisque_binaries, brisque_hiddenimports = collect_all("brisque")

ctk_data = "./.venv/lib/python3.12/site-packages/customtkinter"

a = Analysis(
    ["snap_sweeper/__main__.py"],
    pathex=[os.path.abspath(os.curdir)],  # Ensure the current directory is in the path
    binaries=[
        *libsvm_binaries,
        *chromadb_binaries,
        *brisque_binaries,
    ],
    datas=[
        (ctk_data, "customtkinter/"),
        ("snap_sweeper/resources", "resources/"),
        *libsvm_datas,
        *chromadb_datas,
        *brisque_datas,
    ],
    hiddenimports=[
        *libsvm_hiddenimports,
        *chromadb_hiddenimports,
        *brisque_hiddenimports,
        "snap_sweeper",
        "snap_sweeper.snap_sweeper_app",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=["set_env_vars.py"],  # Add the runtime hook here
    excludes=[],
    noarchive=False,
    optimize=0,
    module_collection_mode={
        "chromadb": "py",
    },
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SnapSweep",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="snap_sweeper/resources/icon.ico",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="SnapSweep",
)
app = BUNDLE(
    coll,
    name="SnapSweep.app",
    bundle_identifier=None,
    icon="snap_sweeper/resources/icon.icns",
)
