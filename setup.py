''' Batch Calculator setup script '''

from setuptools import setup

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
    with open('README.rst') as txt:
        return txt.read()


setup(
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    license=LICENSE,
    name=NAME,
    url=URL,
    version=VERSION,
    entry_points={
        'console_scripts': [
            'zbc = batchcalc.zbc:main',
        ],
    },
    include_package_data=True,
    install_requires=[
        'numpy>=1.8.1',
        'sqlalchemy>=0.9.7',
        'jinja2>=2.7.3',
    ],
    long_description=readme(),
    packages=["batchcalc"],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: MIT',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
    ],
)
