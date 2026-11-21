.. _lsstsso_band:

***************************************
Handling bandpasses with `lsstsso.band`
***************************************

.. currentmodule:: lsstsso.band


Introduction
============

LSSTCam has 6 broadband filters: *u*, *g*, *r*, *i*, *z*, and *y*.  This list of filters is encapsulated into the :class:`~lsstsso.band.Band` class, offering a convenient reference for the filter set and associated data.  The class is derived from the Python `~enum.StrEnum`.

The bands themselves are attributes of the :class:`~lsstsso.band.Band` object:

.. code-block:: python

    >>> from lsstsso import Band
    >>>
    >>> Band.u
    <Band: u, 372.4 nm>
    >>> Band.z
    <Band: z, 868.0 nm>


Looping over ``Band``
=====================

The list of LSSTCam filters may be inspected by passing the class to the `list` function:

.. code-block:: python

    >>> list(Band)
    [<Band: u, 372.4 nm>,
     <Band: g, 480.7 nm>,
     <Band: r, 622.1 nm>,
     <Band: i, 755.9 nm>,
     <Band: z, 868.0 nm>,
     <Band: y, 975.3 nm>]

Notice they are in wavelength order, which can be useful in some contexts.

The :class:`~lsstsso.band.Band` object also be iterated over in a for-loop:

.. code-block:: python

    >>> for band in Band:
    ...     print(band)
    u
    g
    r
    i
    z
    y


Comparing ``Band``
==================

Bands mathematically compare according to wavelength, i.e., ``Band.u`` is less than ``Band.g``:

.. code-block:: python

    >>> Band.u < Band.g
    True

Bands can also be compared to other bands or even strings with the equality operator:

.. code-block:: python

    >>> Band.g == "g"
    True
    >>> Band.g == Band.r
    False


String representations
======================

The string representation is the band name:

.. code-block:: python

    >>> print(Band.r)
    r

The string name can be converted to a band object through initialization:

.. code-block:: python

    >>> Band("y")
    <Band: y, 975.3 nm>


As dictionary keys
==================

:class:`~lsstsso.band.Band` instances can be used as the key in a dictionary:

.. code-block:: python

    >>> m = {Band.u: 21.2, Band.g: 20.1}
    >>> print(m[Band.g])
    20.1

But take care, as the keys are interchangeable with the string values:

    >>> m["u"] = 99.99
    >>> print(m[Band.u])
    99.99


Getting band data
=================

Currently, the only bandpass data is the central wavelength.  It can be accessed with the :attr:`~lsstsso.band.Band.wave` property:

.. code-block:: python

    >>> print(f"The u-band central wavelength is {Band.u.wave}.")
    The u-band central wavelength is 372.4 nm.


Reference/API
=============

.. automodapi:: lsstsso.band
