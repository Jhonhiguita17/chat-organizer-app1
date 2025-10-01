# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules
import os

hidden_imports = collect_submodules('waitress') + collect_submodules('flask') + ['myapp', 'main']

block_cipher = None

a = Analysis(
    scripts=['src/run_waitress.py'],
    pathex=[os.path.abspath('.'), os.path.abspath('src')],
    binaries=[],
    datas=[
        # Carpeta static dentro de networking
        ('src/networking/static', 'networking/static'),
        # Carpeta icons dentro de networking
        ('src/networking/icons', 'networking/icons'),
        # Carpeta templates
        ('src/templates', 'templates'),
        # Carpeta descargas
        ('src/descargas', 'descargas'),
        # Carpeta data con json y logs
        ('data', 'data'),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ChatOrganizerApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ChatOrganizerApp',
)
