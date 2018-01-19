# -*- mode: python -*-

# spec file for PyInstaller for generating windows executables for BC

block_cipher = None


a = Analysis(['batchcalc\\zbc.py'],
             pathex=['C:\\cygwin64\\home\\kasia\\Devel\\batchcalculator\\batchcalc'],
             binaries=None,
             datas=[('C:\\cygwin64\\home\\kasia\\Devel\\batchcalculator\\batchcalc\\data\\zeolite.db', 'data'),
                    ('C:\\cygwin64\\home\\kasia\\Devel\\batchcalculator\\batchcalc\\templates\\tex\\report_color.tex', 'templates\\tex'),
                    ('C:\\cygwin64\\home\\kasia\\Devel\\batchcalculator\\LICENSE.txt', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='BatchCalculator.exe',
          debug=False,
          strip=False,
          upx=False,
          console=False,
          icon='icons\\icon.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='BatchCalculator')
