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

Remotely interact with the Rubin Science Platform
-------------------------------------------------
For ``lsstsso`` to remotely interact with the RSP, you will need to obtain an API access token.  The key only needs read:tap permissions.  Follow the `RSP instructions <https://rsp.lsst.io/guides/auth/creating-user-tokens.html>`_ and save the key to your shell environment with the variable name LSST_SSO_RSP_TOKEN.


Main concepts
=============

``lsstsso`` is organized into a few main sub-modules:

* ``get`` contains functions to get data from the Rubin Science Platform.
* ``color`` contains classes and functions for using and manipulating colors of objects observed by LSST.

Below are a few brief examples show how the package may be used.  First, get a list of comets:

.. doctest-remote-data::

    >>> import lsstsso
    >>> comets = lsstsso.get.comets()
    >>> comets
    <Table length=47>
         ssObjectId     designation   nObs     arc     firstObservationMjdTai tisserand_J permid
                                                d                                               
           int64           str12     int32   float32            Time            float32    str4 
    ------------------- ------------ ----- ----------- ---------------------- ----------- ------
    5785498485624156464    P/1988 D1    11     22.9181     60847.158599118426     2.98857   110P
    ...

Next, get the lightcurve of an object.  The result is based on a join between the SSSource and DiaSource tables:

.. doctest-remote-data::

    >>> lc = lsstsso.get.lightcurve(5785498485624156464)
    >>> lc
    <Table length=11>
         SSObjectId       midpointMjdTai   helioRange topoRange phaseAngle ...
                                               AU         AU       deg     ...
           int64               Time         float32    float32   float32   ...
    ------------------- ------------------ ---------- --------- ---------- ...
    5785498485624156464 60847.158599118426   4.736578  3.751748  3.4085186 ...
    ...

Finally, take a u-g and a g-r color, solve for the u-r color, and transform a u-band magnitude to an r-band magnitude:

    >>> import astropy.units as u
    >>> from lsstsso import Color, ColorMatrix
    >>>
    >>> colors = [
    ...     Color("u", "g", 1.8 * u.mag, 0.01 * u.mag),
    ...     Color("g", "r", 0.5 * u.mag, 0.01 * u.mag),
    ... ]
    >>> cm = ColorMatrix(colors, solve=True)
    >>> print(cm.transform(20.0 * u.mag, 0.02 * u.mag, "u", "r"))
    (<Quantity 17.7 mag>, <Quantity 0.0244949 mag>)
