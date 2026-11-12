.. _lsstsso_rsp:

********************************
Fetching data with `lsstsso.rsp`
********************************

`lsstsso.rsp` fetches data from the Rubin Science Platform (RSP) Table Access Protocol (TAP) services.  This is a lower level interface than `lsstsso.get` that can send any ADQL commands to the RSP and format the result as tabular data.  It can also cache queries locally to avoid repeated interaction with the RSP.

An `lsstsso.rsp.RSP` object handles the authentication, interaction, and job clean-up.  Generally this object is obtained via a context manager:

.. doctest-remote-data::
.. code-block:: python

    >>> from lsstsso.rsp import provider as rsp_provider
    >>>
    >>> with rsp_provider() as rsp:
    ...     # do something

Any valid ADQL query can be sent via the ``RSP`` object.  For example, query the Visit table for DP2 data around a point:

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
    Query not cached ...
    OK in 3.99 s
    Caching result to ...
    >>> print(result)
        visit            ra                dec         band    expMidptMJD     
                        deg                deg                                 
    ------------- ---------------- ------------------- ---- ------------------ 
    2025071100809 52.8114941837909   -28.1345856747246    g  60868.33009929246 


Reference/API
=============

.. automodapi:: lsstsso.rsp
