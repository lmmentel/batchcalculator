
from setuptools import setup
import sys
import wx

APP = "batchcalc/zbc.py"
AUTHOR = "Lukasz Mentel"
AUTHOR_EMAIL = "lmmentel@gmail.com"
DESCRIPTION = "Script for calculating batch composition of zeoliteis"
LICENSE = open('LICENSE.txt').read()
NAME = "batchcalc"
URL = "https://bitbucket.org/lukaszmentel/batchcalc"
VERSION = "0.2.1"
YEAR = "2014"

def readme():
    with open('README.rst') as f:
        return f.read()

RT_MANIFEST = 24

def BuildPy2Exe():
    '''Generate the Py2exe files'''

    try:
        import py2exe
    except ImportError:
        print "\n!! You dont have py2exe installed. !!\n"
        exit()

    OPTS = {"py2exe" : {"compressed" : 1,
                        "optimize" : 1,
                        "bundle_files" : 2,
                        "excludes" : ["Tkinter",],
                        "dll_excludes": ["MSVCP90.dll"]}}

    setup(
        author = AUTHOR,
        author_email = AUTHOR_EMAIL,
        description = DESCRIPTION,
        license = LICENSE,
        name = NAME,
        url = URL,
        version = VERSION,
        options = OPTS,
        windows = [{"script": APP,
                    "icon_resources": [(1, "icons/icon.ico")],
                   }],
    )

    #"other_resources" : [(RT_MANIFEST, 1, manifest)],

def BuildOSXApp():
	'''Build the OSX Applet'''

    # py2app uses this to generate the plist xml for the applet

	copyright = "Copyright {0} {1}".format(AUTHOR, YEAR)
	appid = "com.{0}.{0}".format(NAME)
	PLIST = dict(
			CFBundleName = NAME,
			CFBundleIconFile = 'icons/icon.icns',
			CFBundleShortVersionString = VERSION,
			CFBundleGetInfoString = NAME + " " + VERSION,
			CFBundleExecutable = NAME,
			CFBundleIdentifier = appid,
			CFBundleTypeMIMETypes = ['text/plain',],
			CFBundleDevelopmentRegion = "English",
			NSHumanReadableCopyright = copyright
			)     

	PY2APP_OPTS = dict(
			iconfile = 'icons/icon.icns',
			argv_emulation = False,
			optimize = True,
			plist = PLIST,
			packages = ['batchcalc', 'sqlalchemy', 'jinja2'],
			)
	
	setup(
		app = [APP,],
		author = AUTHOR,
		author_email = AUTHOR_EMAIL,
		description = DESCRIPTION,
		license = LICENSE,
		name = NAME,
		url = URL,
		version = VERSION,
        include_package_data = True,
		options = dict(py2app = PY2APP_OPTS),
		setup_requires = ['py2app'],
        install_requires = [
            'numpy>=1.5.1',
            'sqlalchemy>=0.9.7',
            'jinja2>=2.7.3',
        ],
		) 


def linux_setup():

    setup(
        author = AUTHOR,
        author_email = AUTHOR_EMAIL,
        description = DESCRIPTION,
        license = LICENSE,
        name = NAME,
        url = URL,
        version = VERSION,
        scripts=[
            'batchcalc/zbc.py'],
        include_package_data = True,
        install_requires = [
            'numpy>=1.8.1',
            'sqlalchemy>=0.9.7',
            'jinja2>=2.7.3',
        ],
        long_description = readme(),
        packages = ["batchcalc"],
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'License :: MIT',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 2.7',
        ],
    )

if __name__ == '__main__':

    if wx.Platform == '__WXMSW__':
        # Windows
        BuildPy2Exe()
    elif wx.Platform == '__WXMAC__':
        # OSX
        BuildOSXApp()
    elif wx.Platform == '__WXGTK__':
        linux_setup()
    else:
        print "Unsupported platform: %s" % wx.Platform
