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

* ``get`` contains functions to get data from the RSP.
* ``color`` contains classes and functions for using and manipulating colors of objects observed by LSST.

Below are a few brief examples show how the package may be used.


Getting data from the RSP
-------------------------

First, get a list of comets:

.. doctest-remote-data::
.. code-block:: python

    >>> from lsstsso import get
    >>>
    >>> comets = get.comets()
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
.. code-block:: python

    >>> lc = get.lightcurve(5785498485624156464)
    Querying SSSource INNER JOIN DiaSource
    
    SELECT s.SSObjectId,d.midpointMjdTai,d.ra,d.dec,s.helioRange,s.topoRange,s.phaseAngle,s.elongation,s.ephRate,s.ephOffset,d.band,d.apFlux,d.apFluxErr,d.centroid_flag,d.pixelFlags FROM dp2.SSSource AS s
    INNER JOIN dp2.DiaSource AS d on d.diaSourceId = s.diaSourceId
    WHERE s.SSObjectId = 5785498485624156464
    ORDER BY d.midpointMjdTai
    
    Query not cached ...
    OK in 7.90 s
    Caching result to ...
    >>> print(lc)
         SSObjectId       midpointMjdTai           ra                 dec         helioRange topoRange ...
                                                  deg                 deg             AU         AU    ...
    ------------------- ------------------ ------------------ ------------------- ---------- --------- ...
    5785498485624156464 60847.158599118426  287.2315412417827 -23.851685147435273   4.736578  3.751748 ...
    ...


Working with colors
-------------------

Take a u-g and a g-r color, solve for the u-r color, and transform a u-band magnitude to an r-band magnitude:

.. code-block:: python

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


Forming ADQL statements
-----------------------

Interaction with the RSP Table Access Protocol (TAP) service requires forming ADQL statements.  Related `lsstsso` methods will generally allow one to specify the columns to return, and some will allow query constraints (i.e., the WHERE clause).

For example, use `lsstsso.get.ssobject` to fetch the SSObject IDs for objects with cometary designations and large Jovian Tisserand values:

.. doctest-remote-data::
.. code-block:: python

    >>> comets = get.ssobject(
    ...     "tisserand_J > 3.05 AND designation LIKE 'P/%'",
    ...     columns=["ssObjectId"]
    ... )
    >>> print(comets)
         ssObjectId    
    -------------------
    5785772247091262512
    5785772259674174000


Inspecting results
------------------

Results from the RSP TAP queries are formatted into `~lsstsso.result.Result` objects.  These objects encapsulate tabular data into a slightly more convenient (to me) format by allowing columns to be accessed by member attributes.

For example, with the lightcurve result above one can get the SSObject IDs with:

.. doctest-remote-data::
.. code-block:: python

    >>> lc.ssObjectId
    array([5785498485624156464, 5785498485624156464, 5785498485624156464,
           5785498485624156464, 5785498485624156464, 5785498485624156464,
           5785498485624156464, 5785498485624156464, 5785498485624156464,
           5785498485624156464, 5785498485624156464])

Show all columns in the result:

.. doctest-remote-data::
.. code-block:: python

    >>> lc.columns
    ['SSObjectId',
     'midpointMjdTai',
     'ra',
     'dec',
     'helioRange',
     'topoRange',
     'phaseAngle',
     'elongation',
     'ephRate',
     'ephOffset',
     'band',
     'apFlux',
     'apFluxErr',
     'centroid_flag',
     'pixelFlags']


Cached queries
--------------

TAP queries are cached by default, and the cache used whenever the query string matches the cached query string:

.. doctest-remote-data::
.. code-block:: python

    >>> lc = get.lightcurve(5785498485624156464)
    Querying SSSource INNER JOIN DiaSource
    
    SELECT s.SSObjectId,d.midpointMjdTai,d.ra,d.dec,s.helioRange,s.topoRange,s.phaseAngle,s.elongation,s.ephRate,s.ephOffset,d.band,d.apFlux,d.apFluxErr,d.centroid_flag,d.pixelFlags FROM dp2.SSSource AS s
    INNER JOIN dp2.DiaSource AS d on d.diaSourceId = s.diaSourceId
    WHERE s.SSObjectId = 5785498485624156464
    ORDER BY d.midpointMjdTai
    
    Returning cached result from ...

To skip the caching system, set ``cached=False`` in the keyword arguments:

    >>> lc = get.lightcurve(5785498485624156464, cached=False)  # doctest: +SKIP

To clear the cache, use the `~lsstsso.rsp.RSP` object's ``clean_cache`` function.  By default it removes all cached data.  It can also delete data older than a certain age:

    >>> from lsstsso.rsp import RSP
    >>> RSP.clean_cache()  # doctest: +IGNORE_OUTPUT
    114/114 cache files removed.
