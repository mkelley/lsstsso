LSST SSO documentation
======================

The ``lsstsso`` package contains methods and classes designed for the analysis of Solar System object data from the Legacy Survey of Space and Time (LSST).  It contains convenience wrappers for fetching catalog data from the Rubin Science Platform, functions to help filter that data, and classes for the manipulation of photometric colors.

The data interface is designed in an attempt to be simple and useful in interactive sessions.  If you need something efficient or suitable for large scales, maybe try something else.

Features:
* Query caching.
* Convenience functions for common queries.
* Result objects designed for column-based and row-based inspection.
* Powered by [astropy](https://astropy.org/)!

.. attention::

   ``lsstsso``'s convenience queries are hard coded for DP2.  This and the API will change after the prompt products database is released.

.. toctree::
   :maxdepth: 2
   :hidden:

   getting-started
   user-guide
