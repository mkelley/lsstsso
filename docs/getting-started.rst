.. _getting-started:

***************
Getting Started
***************

.. toctree::
   :maxdepth: 1


Installation
============

You can install ``lsstsso`` and its dependencies using pip::

    python -m pip install git+https://github.com/mkelley/lsstsso

For interaction with the Rubin Science Platform (RSP), you will need to use ``lsstsso`` on the RSP, or connect to the RSP remotely with an API key.

Main concepts
=============

``lsstsso`` is organized into a few main sub-modules::

    * ``get`` contains functions to get data from the Rubin Science Platform.
    * ``color`` contains classes and functions for using and manipulating colors of objects observed by LSST.

A few brief examples show how the package may be used::

    import lsstsso

    lsstsso.
