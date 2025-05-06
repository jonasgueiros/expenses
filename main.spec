# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

a = Analysis(
    ['main.py'],
    pathex=['/.venv'],
    binaries=[],
    datas=[('Despesas', 'Despesas'), ('expenses_db.db', '.')],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,  # Remove or set to None
)

pyz = PYZ(a.pure, a.zipped_data,
    cipher=None)  # Remove or set to None

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='expensys',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='expensys'
)