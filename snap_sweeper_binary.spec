# -*- mode: python ; coding: utf-8 -*-
import os

from PyInstaller.utils.hooks import collect_all, collect_data_files

libsvm_datas, libsvm_binaries, libsvm_hiddenimports = collect_all("libsvm")
chromadb_datas, chromadb_binaries, chromadb_hiddenimports = collect_all("chromadb")
brisque_datas, brisque_binaries, brisque_hiddenimports = collect_all("brisque")
ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all("customtkinter")


snap_sweeper_path = os.path.join(os.path.abspath(os.curdir), "snap_sweeper")

# a = Analysis(
#     ['snap_sweeper/__main__.py'],
#     pathex=[],
#     binaries=[],
#     datas=[],
#     hiddenimports=[],
#     hookspath=[],
#     hooksconfig={},
#     runtime_hooks=[],
#     excludes=[],
#     noarchive=False,
#     optimize=0,
# )
a = Analysis(
    ["snap_sweeper/__main__.py"],
    pathex=[os.path.abspath(os.curdir)],
    binaries=[
        *libsvm_binaries,
        *chromadb_binaries,
        *brisque_binaries,
        *ctk_binaries,
    ],
    datas=[
        ("snap_sweeper/resources", "resources/"),
        *ctk_datas,
        *libsvm_datas,
        *chromadb_datas,
        *brisque_datas,
        (snap_sweeper_path, "snap_sweeper"),
    ],
    hiddenimports=[
        *libsvm_hiddenimports,
        *chromadb_hiddenimports,
        *brisque_hiddenimports,
        *ctk_hiddenimports,
        "snap_sweeper",
        "snap_sweeper.app_manager",
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
    a.binaries,
    a.datas,
    [],
    name="snap_sweeper",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="snap_sweeper/resources/icon.ico",
)
