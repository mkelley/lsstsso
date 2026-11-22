.. _lsstsso_filters:

****************************************
Filtering results with `lsstsso.filters`
****************************************

.. currentmodule:: lsstsso.filters


Finding nearest neighbors
=========================

Catalog query results can be searched for nearest-neighbors with :func:`~lsstsso.filters.sky`:


.. doctest-remote-data::
.. code-block:: python

    >>> import astropy.units as u
    >>> from astropy.coordinates import SkyCoord
    >>> from astropy.table import Table
    >>> from lsstsso import get
    >>> from lsstsso.filters import sky
    >>>
    >>> # cone search the Source catalog around these coordinates:
    >>> coords = SkyCoord([355.424866, 343.418577] * u.deg, [-0.101405, -3.830839] * u.deg)
    >>>
    >>> sources = Table([coords.ra, coords.dec], names=["ra", "dec"])
    >>> result = get.phot_by_positions(sources, table="Source")
    >>> print(len(result))
    3
    >>>
    >>> # find the nearest neighbors to each coordinate
    >>> matched = sky(coords, result)
    >>> print(matched)
     n         coords        nearest             nearest_coords                    sep                 pa
              deg,deg                               deg,deg                       arcsec              rad
    --- -------------------- ------- -------------------------------------- ------------------ -----------------
      0 355.424866,-0.101405       0 355.42485563564344,-0.1013384356784893 0.2425189491551291 6.128721461646556
      1 343.418577,-3.830839       2  343.4185388568125,-3.8307887831488134 0.2268325898828539  5.63466487510969

The nearest column contains the matched indices in the result object, i.e., coordinate number 0 matched result number 0.


Finding nearest neighbors in space and time
===========================================

Catalog results can also be searched for observations within a time tolerance (default is 15 s) using :func:`~lsstsso.filters.sky_and_time`:

.. doctest-remote-data::
.. code-block:: python

    >>> from astropy.time import Time
    >>> from lsstsso.filters import sky_and_time
    >>>
    >>> # times for our search coordinates above
    >>> t = Time([60858.314802, 60935.481232], format="mjd", scale="tai")
    >>>
    >>> # a different object is found for the first coordinate, and nothing for the second:
    >>> matched = sky_and_time(coords, t, result)
    >>> print(matched)
     n         coords             t       nearest             nearest_coords                 nearest_t             dt                 sep                 pa
              deg,deg                                            deg,deg                                           s                 arcsec              deg
    --- -------------------- ------------ ------- -------------------------------------- ----------------- ------------------ ------------------- -----------------
      0 355.424866,-0.101405 60858.314802       1 355.4248380518815,-0.10133548335001005 60858.31480172237 0.0239871209487319 0.26972769086651577 338.0981831329084


Reference/API
=============

.. automodapi:: lsstsso.filters
