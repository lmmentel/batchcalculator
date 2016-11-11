Installation
============

Dependencies
------------

- `Python 2.7.x <https://www.python.org/>`_
- `wxPython <https://wxpython.org/>`_
- `ObjectListView <https://bitbucket.org/wbruhin/objectlistview>`_,
- `reportlab <http://www.reportlab.com/>`_
- `numpy <http://www.numpy.org/>`_
- `jinja2 <http://jinja.pocoo.org/>`_
- `SQLAlchemy <http://www.sqlalchemy.org/>`_


If you want to export your calculations to a `TeX <https://www.tug.org/>`_
report and be able to automatically typeset the pdf you should have a TeX
distribution installed. If you don't know what TeX is `TUG (TeX Users Group)
<https://www.tug.org/>`_ is a good place to start.

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

    $ zbc