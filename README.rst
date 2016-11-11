================
Batch Calculator
================

.. image:: https://travis-ci.org/lmmentel/batchcalculator.svg?branch=master
   :alt: Build Status

.. image:: https://readthedocs.org/projects/batchcalculator/badge/
   :target: https://batchcalculator.readthedocs.org
   :alt: Documentation Status

A GUI script based on `wxPython <http://www.wxpython.org>`_ for calculating the
correct amount of reactants (batch) for a particular zeolite composition given
by the molar ratio of its components.

Installation
============

Prerequisites
-------------

* `Python <https://www.python.org/>`_ 2.7.x,
* `wxPython <http://www.wxpython.org>`_, run and tested with wx version 2.8.12.1,
* `numpy <http://www.numpy.org/>`_, tested with version 1.8.1,
* `SQLAlchemy <http://www.sqlalchemy.org>`_ 0.9.7,
* `Jinja2 <http://jinja.pocoo.org>`_, 2.7.3,
* `reportlab <http://www.reportlab.com/>`_,
* `ObjectListView <https://bitbucket.org/wbruhin/objectlistview>`_,

If you want to export your calculations to a `TeX <https://www.tug.org/>`_
report and be able to automatically typeset the pdf you should have a TeX
distribution installed. If you don't know what TeX is `TUG (TeX Users Group)
<https://www.tug.org/>`_ is a good place to start.

.. for wxPython 3.0.x install libgstreamer-plugins-base-0.10.dev


Installing from source
----------------------
Currently the preferred way is to install the package from source and manually
setup the link and/or shortcuts if you want an launcher on you desktop.

You can either download the code from the `repository
<https://github.com/lmmentel/batchcalculator/releases>`_
and run::

    [sudo] pip install batchcalc-x.x.x.tgz

or::

    [sudo] easy_install batchcalc-x.x.x.tgz

or clone the repository::

    git clone https://github.com/lmmentel/batchcalculator.git

pull the latest version and update::

    git pull

then `cd` to the package directory and run::

    [sudo] python setup.py install

If the installation finishes without errors you should be able to start the GUI
from the command line by typing::

    $ zbc.py

Changelog
=========

v0.3.0 - November 2016
----------------------

Features
^^^^^^^^

* New improved layout, with one output frame and buttons to control scaling
* New option to store, extract, load and export synthesis recipes
* First draft of the `sphinx <http://www.sphinx-doc.org>`_ based documentation
* Database with essential components and chemicals for zeolite synthesis already included

Fixes and improvements
^^^^^^^^^^^^^^^^^^^^^^

* A lot of internal improvements and fixes with considerable simplifications to the code base



v0.1.2 - October 2014
---------------------

* Corrected a bug in the TeX report when rescaling to sample size.
* Updated the database schema for two tables to remove incompatibilities
  when working with sqlitebrowser.
* Updated the chemicals table in the database to include densities, pka, smiles.
* Added an option to change database in the window for calculating the
  composition from masses of reactants.
* Corrected the labels displayed in the ListCtrls.

v0.1.1 - October 2014
---------------------

* Switched completely to `ObjectListView
  <http://sourceforge.net/projects/objectlistview/files/objectlistview-python/v1.2/>`_
  for all the list-type display widgets, in the main window as well as in all
  the relevant dialogs. As a consequence all the dependencies on ListCtrl's
  mixins were dropped.
* Added a function to calculate the zeolite composition (molar ratios) from the
  masses of the reactants.
* Reduced the number of lists displayed in the main window, now there are two
  panels, input and output, and each has two lists.
* Added binaries for Windows and Mac OSX for easier installation.
* Small adjustments to the database.

v0.1.0 - September 2014
-----------------------

* First stable release!

Documentation
=============

The only piece of documentation beyond the code itself is a slide presentation
that can be viewed `here <https://rawgit.com/lmmentel/batchcalculator/master/doc/slides/uio.svg>`_.
The same slides are also included in the repository files under
`/doc/slides/uio.no`.

Help
====

If you have some questions, remarks or requests email me at
`<lmmentel-AT-gmail-DOT-com> <mailto:lmmentel-AT-gmail-DOT-com>`_.

License
=======

The MIT License (MIT)

Copyright (c) 2014 Lukasz Mentel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
