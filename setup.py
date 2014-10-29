
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
VERSION = "0.1.2"
YEAR = "2014"

def readme():
    with open('README.rst') as f:
        return f.read()


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
