# -*- mode: python -*-

block_cipher = None

def Datafiles(*filenames, **kw):
    import os
    
    def datafile(path, strip_path=True):
        parts = path.split('/')
        path = name = os.path.join(*parts)
        if strip_path:
            name = os.path.basename(path)
        return name, path, 'DATA'

    strip_path = kw.get('strip_path', True)
    return TOC(
        datafile(filename, strip_path=strip_path)
        for filename in filenames
        if os.path.isfile(filename))

docfiles = Datafiles('LICENSE.txt')
dbfile = Datafiles('batchcalc/data/zeolite.db', strip_path=False) # keep the path of this file
tmpfiles = Datafiles('batchcalc/templates/tex/report_color.tex', strip_path=False)

a = Analysis(['batchcalc/zbc.py'],
             pathex=['C:\\cygwin\\home\\lmentel\\devel\\batchcalculator'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None,
             cipher=block_cipher)
pyz = PYZ(a.pure,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='BatchCalculator.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False , icon='icons\\icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
	       docfiles,
	       dbfile,
               tmpfiles,
               strip=None,
               upx=True,
               name='BatchCalculator')
