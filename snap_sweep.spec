# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

libsvm_datas, libsvm_binaries, libsvm_hiddenimports = collect_all("libsvm")

ctk_data = "./.venv/lib/python3.12/site-packages/customtkinter"

a = Analysis(
    ["snap_sweep/__main__.py"],
    pathex=[],
    binaries=libsvm_binaries,
    datas=[
        (ctk_data, "customtkinter/"),
        ("snap_sweep/themes", "snap_sweep/themes"),
        *libsvm_datas,
    ],
    hiddenimports=[*libsvm_hiddenimports, "snap_sweep"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=["set_env_vars.py"],  # Add the runtime hook here
    excludes=[],
    noarchive=False,
    optimize=0,
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
    icon=None,
    bundle_identifier=None,
)
