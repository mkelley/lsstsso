.. _lsstsso_rsp:

********************************
Fetching data with `lsstsso.rsp`
********************************

.. currentmodule:: lsstsso.rsp


Introduction
============

:mod:`lsstsso.rsp` fetches data from the Rubin Science Platform (RSP) Table Access Protocol (TAP) services.  This is a lower level interface than `lsstsso.get` that can send any ADQL commands to the RSP and format the result as tabular data.  It can also cache queries locally to avoid repeated interaction with the RSP.

An :class:`~lsstsso.rsp.RSP` object handles the authentication, interaction, and job clean-up.  Generally this object is obtained via a context manager:

.. doctest-remote-data::
.. code-block:: python

    >>> from lsstsso.rsp import provider as rsp_provider
    >>>
    >>> with rsp_provider() as rsp:
    ...     ... # do something

Any valid ADQL query can be sent via the :class:`~lsstsso.rsp.RSP` object.  For example, query the Visit table for DP2 data around a point:

.. doctest-remote-data::
.. code-block:: python

    >>> query = """
    ... SELECT visit, ra, dec, band, expMidptMJD
    ... FROM dp2.Visit
    ... WHERE CONTAINS(
    ...       POINT('ICRS', ra, dec),
    ...       CIRCLE('ICRS', 53.13, -28.10, 3)
    ...     ) = 1
    ...   AND band IN ('g', 'r')
    ... ORDER BY expMidptMJD ASC
    ... """
    >>>
    >>> with rsp_provider() as rsp:
    ...     result = rsp.query_tap(query)
    >>> print(result)
        visit            ra                dec         band    expMidptMJD
                        deg                deg
    ------------- ---------------- ------------------- ---- ------------------
    2025071100809 52.8114941837909   -28.1345856747246    g  60868.33009929246
    ...


Cached queries
==============

All TAP queries are cached by default, and the cache used whenever the query string matches the cached query string.  To clear the cache, use the :class:`~lsstsso.rsp.RSP` object's :func:`~lsstsso.rsp.RSP.clean_cache` function.  By default it removes all cached data.  It can also delete data older than a certain age:

    >>> from lsstsso.rsp import RSP
    >>> RSP.clean_cache()  # doctest: +SKIP
    114/114 cache files removed.


Reference/API
=============

.. automodapi:: lsstsso.rsp
