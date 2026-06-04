# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller packaging config for DiligenceBinder Windows exe."""

import sys
from pathlib import Path

block_cipher = None

# Do not bundle .env or API keys into the executable.
datas = []

# 隐藏导入 (PyInstaller 可能检测不到的模块)
hiddenimports = [
    "fitz",           # PyMuPDF
    "openpyxl",       # Excel
    "requests",       # HTTP
    "urllib3",
    "certifi",
    "charset_normalizer",
    "idna",
    "json",
    "re",
    "pathlib",
    "io",
    "tkinter",
    "tkinter.filedialog",
    "tkinter.messagebox",
    "tkinter.ttk",
    "webbrowser",
    "threading",
]

a = Analysis(
    ["launcher.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="DiligenceBinder",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,       # Windows: 不显示命令行窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,           # 可添加 .ico 图标路径
)
