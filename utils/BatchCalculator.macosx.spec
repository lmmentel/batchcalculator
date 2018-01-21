# -*- mode: python -*-

block_cipher = None


a = Analysis(['batchcalc/zbc.py'],
             pathex=['/Users/lukaszmentel/Devel/batchcalculator'],
             binaries=[],
             datas=[('/Users/lukaszmentel/Devel/batchcalculator/batchcalc/data/zeolite.db', 'data'),
                    ('/Users/lukaszmentel/Devel/batchcalculator/batchcalc/templates/tex/report_color.tex', 'templates/tex'),
                    ('/Users/lukaszmentel/Devel/batchcalculator/LICENSE.txt', '.')],
             hiddenimports=['sqlalchemy.ext.baked',],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure,
          a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='BatchCalculator',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False)

app = BUNDLE(exe,
             name='BatchCalculator.app',
             icon='/Users/lukaszmentel/Devel/batchcalculator/icons/icon.icns',
             bundle_identifier=None)
