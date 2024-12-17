# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\54414\\Desktop\\软件工程项目\\SE1\\server.py'],
    pathex=[],
    binaries=[],
    datas = [
    ('chat_history.json', '.'),
    ('package.json', '.'),
    ('package-lock.json', '.'),
    ('router_api.py', '.'),
    ('__pycache__', '__pycache__'),
    ('chain_wrapper', 'chain_wrapper'),
    ('node_modules', 'node_modules'),
    ('static', 'static')
],
    hiddenimports=['pydantic','pydantic-core','pydantic.deprecated.decorator'],
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
    name='诗享人生',
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
    icon=[],
)
