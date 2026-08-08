# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['c:\\Users\\Administrator\\.trae-cn\\work\\6a709f9b0cee8b878aeb991b\\build_onedir_final\\plc_io_random_allocator.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
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
    name='PLC_IO_RandomAllocator',
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
    icon=['c:\\Users\\Administrator\\.trae-cn\\work\\6a709f9b0cee8b878aeb991b\\build_onedir_final\\app_icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PLC_IO_RandomAllocator',
)