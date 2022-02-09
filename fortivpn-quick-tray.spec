# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['indicator.py'],
             pathex=['/home/user/projects/my-repos/fortivpn-quick-tray-qt'],
             binaries=[],
             datas=[('./icons/*.png', 'icons'), ('version', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['PySide2.QtQml', 'PySide2.QtNetwork'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='fortivpn-quick-tray',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
