.. _lsstsso_get:

********************************
Fetching data with `lsstsso.get`
********************************

Introduction
============

`lsstsso.get` fetches data from the Rubin Science Platform (RSP).  The methods are slightly higher level interfaces than plain SQL/ADQL queries.  They are centered around observations of Solar System objects, but may be usable in other contexts.

.. attention::

   `lsstsso` is exclusively coded to Data Preview 2.  This will likely change after the Prompt Products Database is made public.

The `lsstsso.get` module is currently designed for the `Data Preview 2 <https://sdm-schemas.lsst.io/dp2.html>`_ catalogs.  Fetching data from other `Science Data Model Schemas <https://sdm-schemas.lsst.io/>`_ should be possible with the `lsstsso.rsp` submodule.

You'll want to have those [RSP DP2 schemas](https://sdm-schemas.lsst.io/dp2.html) on hand for reference.


Query the SSObject table
========================

The SSObject table may be queried with `lsstsso.get.ssobject`.  Constraints on the query are required, formatted as the WHERE clause in the ADQL query.  SSObject columns may be prefixed with "s.", numbered_identifications may be prefixed with "n.", e.g., "s.ssObjectId".  For example, to get the SSObject with a specific ID:

.. doctest-remote-data::
.. code-block:: python

    >>> from lsstsso import get
    >>> 
    >>> result = get.ssobject("ssObjectId = 5785498485624156464")
    >>> print(result)
         ssObjectId     designation nObs   arc   firstObservationMjdTai tisserand_J permid
                                            d              d                              
    ------------------- ----------- ---- ------- ---------------------- ----------- ------
    5785498485624156464   P/1988 D1   11 22.9181     60847.158599118426     2.98857   110P

Or, to get 10 objects with Jovian Tisserand values less than 2.9:

.. doctest-remote-data::
.. code-block:: python

    >>> result = get.ssobject("s.tisserand_J < 2.9", top=10)
    >>> print(result)
         ssObjectId     designation  nObs    arc    firstObservationMjdTai tisserand_J permid
                                              d               d                              
    ------------------- ------------ ---- --------- ---------------------- ----------- ------
      21163611629041485   2001 QM257    2   1.00661     60878.327588625485     2.84469 109549
    ...


Get a list of comets
====================

Get a list of all SSObjects with cometary designations, i.e., identifications starting with C/, P/, or A/.  A/ objects are technically asteroidal, but are have orbits that are dynamically similar to comets, and so are included here.

The query is based on a join between the `SSObject <https://sdm-schemas.lsst.io/dp2.html#SSObject>`_ and `numbered_identifications <https://sdm-schemas.lsst.io/dp2.html#numbered_identifications>`_ tables.

.. doctest-remote-data::
.. code-block:: python

    >>> comets = get.comets()
    >>> print(comets)
         ssObjectId     designation  nObs     arc     firstObservationMjdTai tisserand_J permid
                                               d                d                              
    ------------------- ------------ ---- ----------- ---------------------- ----------- ------
    5785498485624156464    P/1988 D1   11     22.9181     60847.158599118426     2.98857   110P
    ...


Get the lightcurve of an object
===============================

With the SSObjectID of an object, one can get the linked SSSource/DiaSource photometry:

.. doctest-remote-data::
.. code-block:: python

    >>> lc = get.lightcurve(5785498485624156464)
    >>> print(lc)
         SSObjectId       midpointMjdTai           ra                 dec         helioRange topoRange ...
                                                  deg                 deg             AU         AU    ...
    ------------------- ------------------ ------------------ ------------------- ---------- --------- ...
    5785498485624156464 60847.158599118426  287.2315412417827 -23.851685147435273   4.736578  3.751748 ...
    ...


Query the MPC orbit table
=========================

The Minor Planet Center's orbit table is on the RSP, and may be queried with `lsstsso.get.orbit`:

.. doctest-remote-data::
.. code-block:: python

    >>> orbit = get.orbit("designation = 'P/1988 D1'")
    >>> print(orbit)
    designation epoch_mjd  a         q                 e                i         ...
                           AU        AU                                deg        ...
    ----------- --------- --- ---------------- ----------------- ---------------- ...
      P/1988 D1   61000.0 0.0 2.45298759313139 0.319253973199543 11.7119257450699 ...

Query for photometry by sky position
====================================

`lsstsso.get.phot_by_positions` is used to get photometry for a list of sky positions.  The positions are uploaded as a table and a small cone search is executed around each one.  Either the Source or the DiaSource columns may be queried.  The results will be joined with the `VisitDetector table <https://sdm-schemas.lsst.io/dp2.html#VisitDetector>`_ so that observational metadata may also be obtained (e.g., seeing):

.. attention::

    Take care with RA values.  At the time of writing (Nov 2026), values below 0 fail.

.. doctest-remote-data::

    >>> import astropy.units as u
    >>> from astropy.table import Table
    >>>
    >>> ra = [287.2315412417827] * u.deg
    >>> dec = [-23.851685147435273] * u.deg
    >>> sources = Table([ra, dec], names=["ra", "dec"])
    >>>
    >>> result = get.phot_by_positions(sources)
    >>> print(result)
         query_ra          query_dec              ra                dec         band ...
           deg                deg                deg                deg              ...
    ----------------- ------------------- ----------------- ------------------- ---- ...
    287.2315412417827 -23.851685147435273 287.2315412417827 -23.851685147435273    i ...

With the ephemeris positions of a target obtained by other means, `lsstsso.get.phot_by_positions` can get photometry of any Solar System object, even if they are not linked to the object by Rubin Observatory's Solar System Processing.


Reference/API
=============

.. automodapi:: lsstsso.get
