# -*- mode: python -*-

block_cipher = None


a = Analysis(['PyVASCO.py'],
             pathex=['C:\\Users\\paribesm\\PyCharmProjects\\PyVASCO_v2.0\\PyVASCO\\PyVASCO_Code'],
             binaries=[],
             datas=[],
             hiddenimports=['pandas._libs.tslibs.np_datetime','pandas._libs.tslibs.nattype','pandas._libs.skiplist','scipy._lib.messagestream'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['PyQt5'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='PyVASCO',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True,
	  icon='Icon.ico')