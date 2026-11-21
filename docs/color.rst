.. _lsstsso_color:

***********************************************************
Color measurements and transformations with `lsstsso.color`
***********************************************************

.. currentmodule:: lsstsso.color


Introduction
============

``lsstsso`` has classes and functions designed for analysis of broadband colors from LSSTCam and the LSST.  One can represent color measurements in the |Color| class, transform between colors with a |ColorMatrix|, and even fill in missing color measurements, e.g., calculate :math:`g-r` from :math:`u-r` and :math:`u-g`, with correlated uncertainties using :func:`~lsstsso.color.measure` and :func:`~lsstsso.color.solve`.


Color measurements with Color
=============================

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

The bands are saved as the ``left`` and ``right`` attributes, the value and uncertainty as ``index`` and ``unc``:

.. code-block:: python

    >>> color.left
    <Band: g, 480.7 nm>
    >>> color.right
    <Band: r, 622.1 nm>
    >>> color.index
    <Quantity 0.55 mag>
    >>> color.unc
    <Quantity 0.01 mag>


Averaging colors
================

When |Color| objects contain an array of values, they may be weighted by their uncertainties and averaged together with :func:`~lsstsso.color.Color.mean`:

.. code-block:: python

    >>> color = Color("g", "r", [0.54, 0.58, 0.6], [0.01, 0.03, 0.03])
    >>> color.mean()
    <Color: g-r = 0.549 ± 0.009 mag>


Multiple colors with ColorMatrix
================================

The |ColorMatrix| class is used to hold multiple colors of an object.  Internally the colors are stored as a flat array, but conceptually the colors form a 2D array:

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
    >>> cm = ColorMatrix.from_colors(colors)
    >>> cm
    <ColorMatrix: 5 values>
    >>> print(cm)
    u-g = 1.210 ± 0.010 mag
    g-i = 0.540 ± 0.010 mag
    g-z = 0.550 ± 0.010 mag
    r-i = 0.120 ± 0.010 mag
    i-y = 0.020 ± 0.010 mag

Colors can also be accessed with a key-based look-up:

.. code-block:: python

    >>> cm["g", "z"]
    <Color: g-z = 0.550 ± 0.010 mag>

Indexing with colors that are not defined returns ``None``:

.. code-block:: python

    >>> cm["i", "z"] is None
    True

This color matrix has 5 values.  There are the 15 possible values in the LSSTCam filter set.  The colors are directly accessible from the 15-element ``index`` attribute:

.. code-block:: python

    >>> print(cm.index)
    [1.21 -- -- -- -- -- 0.54 0.55 -- 0.12 -- -- -- 0.02 --]

Note that ``index`` is a :class:`numpy.ma.MaskedArray`, with undefined colors masked.

Similarly, the ``cov`` attribute, a 15×15 element 2D array, stores the covariance matrix.  For convenience, the 1-σ uncertainties on each color can be accessed from the ``unc`` attribute.

.. code-block:: python

    >>> print(cm.unc)
    [0.01 -- -- -- -- -- 0.01 0.01 -- 0.01 -- -- -- 0.01 --]

The mapping between index and color can be discovered with the :func:`~lsstsso.color.ColorMatrix.bands_to_array_index` and :func:`~lsstsso.color.ColorMatrix.array_index_to_bands` functions.

For convenience, the covariance between two colors can be returned from :func:`~lsstsso.color.ColorMatrix.covariance`, but in this example the covariance was not defined, so the value is ``masked``:

.. code-block:: python

    >>> cm.covariance(["u", "g"], ["g", "i"])
    masked

Finally, the |ColorMatrix| can be used as an iterable for the defined colors:

.. code-block:: python

    >>> for color in cm:
    ...     print(color)
    u-g = 1.210 ± 0.010 mag
    g-i = 0.540 ± 0.010 mag
    g-z = 0.550 ± 0.010 mag
    r-i = 0.120 ± 0.010 mag
    i-y = 0.020 ± 0.010 mag


Calculating colors from data
============================

Colors can be calculated from an array of brightness measurements with :func:`~lsstsso.color.measure`, which returns a |ColorMatrix| object:

.. code-block:: python

    >>> from lsstsso.color import measure
    >>>
    >>> m = [16.5, 16.0, 16.4]
    >>> unc = [0.01, 0.01, 0.01]
    >>> bands = ["u", "r", "g"]
    >>>
    >>> cm = measure(m, unc, bands)
    >>> print(cm)
    u-g = 0.100 ± 0.014 mag
    u-r = 0.500 ± 0.014 mag
    g-r = 0.400 ± 0.014 mag

:func:`~lsstsso.color.measure` returns every color that can be directly measured, even if they are not independent from the others.  The correlations between colors are stored in the |ColorMatrix| object.


Refining colors
===============

Take for example, three independently measured colors, :math:`u-g=1.29\pm0.10` mag, :math:`u-r=1.65\pm0.01`, and :math:`g-r=0.41\pm0.02`.  We can improve the uncertainty on :math:`u-g` with information from the other two measurements, which have much smaller uncertainties.  This is done with :func:`lsstsso.color.solve`.  The function uses a Generalized Least Squares technique that accounts for correlations between colors:

.. code-block:: python

    >>> from lsstsso.color import Color, ColorMatrix, solve
    >>>
    >>> colors = [
    ...     Color("u", "g", 1.29, 0.10),
    ...     Color("u", "r", 1.65, 0.01),
    ...     Color("g", "r", 0.41, 0.02),
    ... ]
    >>> cm = solve(ColorMatrix.from_colors(colors))
    >>> print(cm)
    u-g = 1.242 ± 0.022 mag
    u-r = 1.650 ± 0.010 mag
    g-r = 0.408 ± 0.020 mag

But take care, as now the measurements are correlated:

.. code-block:: python

    >>> print(cm.covariance(["u", "g"], ["g", "r"]))
    -0.00038095238095238096


Calculating colors
==================

The following color set is missing :math:`g-r` and :math:`z-y` values, but they can be calculated from the other colors, e.g., :math:`g-r = u-r - u-g` and :math:`g-r = g-i + r-i`.  Here, we solve for the missing colors with :func:`lsstsso.color.solve`:

.. code-block:: python

    >>> from lsstsso.color import Color, ColorMatrix, solve
    >>>
    >>> colors = [
    ...     Color("u", "g", 1.21, 0.01),
    ...     Color("g", "i", 0.54, 0.01),
    ...     Color("g", "z", 0.55, 0.01),
    ...     Color("r", "i", 0.12, 0.01),
    ...     Color("i", "y", 0.02, 0.01),
    ... ]
    >>> cm = ColorMatrix.from_colors(colors)
    >>> cm["g", "r"] is None
    True
    >>> cm["z", "y"] is None
    True
    >>> cm = solve(cm)
    >>> cm["g", "r"]
    <Color: g-r = 0.420 ± 0.014 mag>
    >>> cm["z", "y"]
    <Color: z-y = 0.010 ± 0.017 mag>

As in the previous example, the solved colors may now have correlated uncertainties.

Compare the variance on :math:`g-r` to the covariance between :math:`g-r` and :math:`g-i`:

.. code-block:: python

    >>> print(cm.covariance(("g", "r"), ("g", "r")))  # pytest: +FLOAT_CMP
    0.0002
    >>> print(cm.covariance(("g", "r"), ("g", "i")))  # pytest: +FLOAT_CMP
    0.0001


Transforming between bandpasses
===============================

With a |ColorMatrix| one can convert observations to other bandpasses using :func:`~lsstsso.color.transform`:

.. code-block:: python

    >>> import astropy.units as u
    >>> from lsstsso.color import Color, ColorMatrix, transform
    >>>
    >>> m = [18.20, 17.0, 16.58] * u.mag
    >>> unc = [0.1, 0.03, 0.02] * u.mag
    >>> bands = ["u", "g", "r"]
    >>>
    >>> colors = [
    ...     Color("u", "r", 1.62, 0.01),
    ...     Color("g", "r", 0.42, 0.01),
    ... ]
    >>> cm = ColorMatrix.from_colors(colors)
    >>> m2, unc2 = cm.transform(m, unc, bands, "r")
    >>> print(m2)
    [16.58 16.58 16.58] mag


Read and write |ColorMatrix| to a file
======================================

Color matrices may be written to and read from files.  They are written as ASCII tables with an ECSV format, which is able to save and restore data masks:

.. code-block:: python

    >>> cm.write("colors.ecsv")  # doctest: +SKIP
    >>> new_cm = ColorMatrix.read("colors.ecsv")  # doctest: +SKIP


Reference/API
=============

.. automodapi:: lsstsso.color
    :include-all-objects:
