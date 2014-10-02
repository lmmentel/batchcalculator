========================
Zeolite Batch Calculator
========================

A GUI script based on `wxPython <http://www.wxpython.org>`_ for calculating the
correct amount of reagents (batch) for a particular zeolite composition given
by the molar ratio of its components.

Installation
============

Prerequisites
-------------

* `python <https://www.python.org/>`_ 2.7.x,
* `wxPython <http://www.wxpython.org>`_, run and tested with wx version 2.8.12.1,
* `numpy <http://www.numpy.org/>`_, tested with version 1.8.1,
* `SQLAlchemy <http://www.sqlalchemy.org>`_ 0.9.7,
* `Jinja2 <http://jinja.pocoo.org>`_, 2.7.3,

.. for wxPython 3.0.x install libgstreamer-plugins-base-0.10.dev


Installing from source
----------------------
Currently the preferred way is to install the package from source and manually
setup the link and/or shortcuts if necessary.

You can either download the code from the `repository
<https://github.com/lmmentel/batchcalculator/releases>`_
and run::

    [sudo] pip install batchcalc-x.x.x.tgz

or clone the repository::

    git clone https://github.com/lmmentel/batchcalculator.git

pull the latest version and update::

    git pull

then `cd` to the package directory and run::

    [sudo] python setup.py install

If installation finishes without errors you should be able to start the GUI
from the command line by typing::

    $ zbc.py

Documentation
=============

The only piece of documentation beyond the code itself is a slide presentation
that can be found in this repository under `doc/slides/uio.svg`.

Help
====

If you have some questions, remarks or requests email me at
`<lmmentel@gmail.com> <mailto:lmmentel@gmail.com>`_.

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
