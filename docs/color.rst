.. _lsstsso_color:

***********************************************************
Color measurements and transformations with `lsstsso.color`
***********************************************************

Introduction
============

``lsstsso`` has classes and functions designed for analysis of broadband colors from LSSTCam and the LSST.  One can represent color measurements in the |Color| class, transform between colors with a |ColorMatrix|, and even fill in missing color measurements, e.g., calculate :math:`g-r` from :math:`u-r` and :math:`u-g`, with uncertainties.


Color measurements
==================

Broadband colors are represented by 4 parameters: two filters, a measurement, and an uncertainty.  The |Color| can carry these parameters together in one object in units of magnitude.

Create a *g*–*r* color measurement of 0.55 ± 0.01 mag:

.. code-block:: python

    >>> import astropy.units as u
    >>> from lsstsso import Band, Color
    >>>
    >>> color = Color(Band.g, Band.r, 0.55 * u.mag, 0.01 * u.mag)
    >>> print(color)
    g-r = 0.550 ± 0.010 mag

For convenience, |Color| may be initialized with strings and floats:

.. code-block:: python

    >>> color = Color("g", "r", 0.55, 0.01)
    >>> print(color)
    g-r = 0.550 ± 0.010 mag

The bands are saved as the ``left`` and ``right`` attributes:

.. code-block:: python

    >>> color.left
    <Band: g, 480.7 nm>
    >>> color.right
    <Band: r, 622.1 nm>

The value and uncertainty are the ``index`` and ``unc`` attributes:

.. code-block:: python

    >>> color.index
    <Quantity 0.55 mag>
    >>> color.unc
    <Quantity 0.01 mag>

Colors and be calculated from an array of brightness measurements:

.. code-block:: python

    >>> from lsstsso.color import measure
    >>>
    >>> m = [16.5, 16.0, 16.4]
    >>> unc = [0.01, 0.01, 0.01]
    >>> bands = ["u", "r", "g"]
    >>>
    >>> print(measure(m, unc, bands))
    [<Color u-g = 0.100 ± 0.014 mag>, <Color g-r = 0.400 ± 0.014 mag>]

.. attention::

    The colors calculated from more than three bands will have correlated uncertainties, but these are not yet calculated by :func:`~lsstsso.color.measure`.


Multiple colors
===============

The |ColorMatrix| class is used to hold multiple colors of an object.  The colors are stored in a 2D array:

.. math::

    \begin{bmatrix}
      0 & u-g & u-r & u-i & u-z & u-y \\
    g-u &   0 & g-r & g-i & g-z & g-y \\
    r-u & r-g &   0 & r-i & r-z & r-y \\
    i-u & i-g & i-r &   0 & i-z & i-y \\
    z-u & z-g & z-r & z-i &   0 & z-y \\
    y-u & y-g & y-r & y-i & y-z &   0 \\
    \end{bmatrix}

First, create a |ColorMatrix| with multiple color measurements of the Sun from Willmer (2018):

.. code-block:: python

    >>> from lsstsso import ColorMatrix
    >>>
    >>> colors = [
    ...     Color("u", "g", 1.21, 0.01),
    ...     Color("g", "i", 0.54, 0.01),
    ...     Color("g", "z", 0.55, 0.01),
    ...     Color("r", "i", 0.12, 0.01),
    ...     Color("i", "y", 0.02, 0.01),
    ... ]
    >>> cm = ColorMatrix(colors)
    >>> cm
    <ColorMatrix: 5 values>

The color matrix has 5 values, accessible from the ``index`` and ``unc`` attributes:

.. code-block:: python

    >>> print(cm.index)
    [[-- 1.21 -- -- -- --]
     [-1.21 -- -- 0.54 0.55 --]
     [-- -- -- 0.12 -- --]
     [-- -0.54 -0.12 -- -- 0.02]
     [-- -0.55 -- -- -- --]
     [-- -- -- -0.02 -- --]]
    >>> print(cm.unc)
    [[-- 0.01 -- -- -- --]
     [0.01 -- -- 0.01 0.01 --]
     [-- -- -- 0.01 -- --]
     [-- 0.01 0.01 -- -- 0.01]
     [-- 0.01 -- -- -- --]
     [-- -- -- 0.01 -- --]]

The index is a NumPy :class:`~numpy.ma.MaskedArray`, and undefined values are masked.  Colors can be accessed from the array

.. code-block:: python

    >>> print(cm.index[0, 1])
    1.21

Or through the bracket notation, which returns a |Color| instance:

.. code-block:: python

    >>> cm["u", "g"]
    <Color u-g = 1.210 ± 0.010 mag>

Finally, the |ColorMatrix| can be used as an iterable for the defined colors:

.. code-block:: python

    >>> for color in cm:
    ...     print(color)
    u-g = 1.210 ± 0.010 mag
    g-i = 0.540 ± 0.010 mag
    g-z = 0.550 ± 0.010 mag
    r-i = 0.120 ± 0.010 mag
    i-y = 0.020 ± 0.010 mag


Averaging colors
================

When |Color| objects contain an array of values, they may be weighted by their uncertainties and averaged together with :func:`~lsstcolor.color.color.Color.mean`:

.. code-block:: python

    >>> color = Color("g", "r", [0.54, 0.58, 0.6], [0.01, 0.03, 0.03])
    >>> color.mean()
    <Color g-r = 0.549 ± 0.009 mag>

Initializing a |ColorMatrix| from a list of colors will also average them together, if needed:

.. code-block:: python

    >>> colors = [
    ...     Color("g", "r", [0.54, 0.58, 0.6], [0.01, 0.03, 0.03]),
    ...     Color("r", "i", 0.21, 0.01),
    ...     Color("r", "i", 0.26, 0.03),
    ... ]
    >>> cm = ColorMatrix(colors)
    >>> cm["g", "r"]
    <Color g-r = 0.549 ± 0.009 mag>
    >>> cm["r", "i"]
    <Color r-i = 0.215 ± 0.009 mag>


Extrapolating colors
====================

The following color set is missing :math:`g-r` and :math:`z-y` values, but they can be calculated from the other colors, e.g., :math:`g-r = u-r - u-g` and :math:`g-r = g-i + r-i`.  The missing colors can be solved for by :math:`\chi^2` minimization with :func:`lsstsso.color.solve`:

.. code-block:: python

    >>> from lsstsso.color import solve
    >>>
    >>> colors = [
    ...     Color("u", "g", 1.21, 0.01),
    ...     Color("g", "i", 0.54, 0.01),
    ...     Color("g", "z", 0.55, 0.01),
    ...     Color("r", "i", 0.12, 0.01),
    ...     Color("i", "y", 0.02, 0.01),
    ... ]
    >>> cm = ColorMatrix(colors)
    >>> cm["g", "r"]
    masked
    >>> cm["z", "y"]
    masked
    >>> cm, cov, cov_colors = solve(colors)
    >>> cm["g", "r"]
    <Color g-r = 0.420 ± 0.014 mag>
    >>> cm["z", "y"]
    <Color z-y = 0.010 ± 0.017 mag>

The solved colors will generally have correlated uncertainties.  The covariance matrix and the colors for the columns and rows are also returned by ``solve``.

Compare the variance on :math:`g-r` to the covariance between :math:`g-r` and :math:`g-i`:

.. code-block:: python

    >>> print(cov_colors)
    [('u', 'g'), ('u', 'r'), ('u', 'i'), ('u', 'z'), ('u', 'y'), ('g', 'r'), ('g', 'i'), ('g', 'z'), ('g', 'y'), ('r', 'i'), ('r', 'z'), ('r', 'y'), ('i', 'z'), ('i', 'y'), ('z', 'y')]
    >>> i = cov_colors.index(("g", "r"))
    >>> print(cov[i, i])
    0.00019999999999999998
    >>> j = cov_colors.index(("g", "i"))
    >>> print(cov[i, j])  # pytest: +FLOAT_CMP
    9.999999999999999e-05


Reference/API
=============

.. automodapi:: lsstsso.color
    :include-all-objects:
