===========
Preparation
===========

Dependencies
============

In order to use ``simpleapi``, you must have Python and at least django or Flask installed. If you're using Python <= 2.5 you have to install ``simplejson`` by::

    pip install --upgrade simplejson

Python >= 2.6 contains a built-in json module which already fits our needs.

Installation
============

PyPI
----

You can either install a *stable* version of ``simpleapi`` from PyPI using ``easy_install`` or ``pip``::

    easy_install -U simpleapi

*or*
::

    pip install simpleapi

GitHub
------

If you're brave you can use the latest **development** version::

    git clone git://github.com/flosch/simpleapi.git

**Please consider yourself warned:** The bleeding edge version might contain
bugs, new features, backward-incompatibility issues and more problems you
might not think of.

Manual Setup
------------

If you don't like one of the easy ways to install ``simpleapi``, you can also
`download the latest version of simpleapi  <http://github.com/flosch/simpleapi/downloads>`_ from GitHub as an tgz or
zip file.

To install ``simpleapi`` on your computer, unpack the compressed file and run::

    python setup.py install

Depending on your system's configuration, you must be an administrator to install ``simpleapi``.