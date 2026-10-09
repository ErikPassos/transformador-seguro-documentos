# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

pandas_datas, pandas_bins, pandas_hidden = collect_all("pandas")
openpyxl_datas, openpyxl_bins, openpyxl_hidden = collect_all("openpyxl")
pdfplumber_datas, pdfplumber_bins, pdfplumber_hidden = collect_all("pdfplumber")

hiddenimports = pandas_hidden + openpyxl_hidden + pdfplumber_hidden
binaries = pandas_bins + openpyxl_bins + pdfplumber_bins
datas = pandas_datas + openpyxl_datas + pdfplumber_datas

a = Analysis(
    ["interface.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name="TransformadorSeguro",
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
    icon=["recursos\\icone.ico"] if __import__("os").path.exists("recursos\\icone.ico") else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="TransformadorSeguro",
)
