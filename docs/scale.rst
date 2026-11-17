.. _lsstsso_scale:

*****************************************
Scaling observations with `lsstsso.scale`
*****************************************


Introduction
============

Photometry of Solar System objects commonly need to be scaled to consistent circumstances for analysis.  This module includes some functions to assist with that scaling.


Scale by geometry
=================


Reduced magnitude
-----------------

With :func:`lsstsso.scale.geometry`, one can correct for observational geometry.  The default is to calculate scale factors for reduced magnitude, :math:`H(1, 1, α)`, i.e., :math:`1/r^2` scaling to correct to a heliocentric distance of 1 au and a observer-target distance of 1 au, leaving the phase effect uncorrected:

.. code-block:: python

    >>> import astropy.units as u
    >>> from lsstsso import scale
    >>>
    >>> rh = [1, 2, 4] * u.au
    >>> delta = [1, 2, 3] * u.au
    >>> 
    >>> s = scale.geometry(rh, delta)
    >>> print(s)  # pytest: +FLOAT_CMP
    [0.         3.01029996 5.39590623] mag

With these scale factors, convert reduced magnitude to apparent magnitude:

.. code-block:: python

    >>> H11a = 5.0 * u.mag
    >>> m = H11a + s
    >>> print(m)
    [ 5.          8.01029996 10.39590623] mag


Absolute magnitude
------------------

To account for phase effect and get scale factors for absolute magnitude, :math:`H(1, 1, 0)`, provide the phase angles and a phase function:

.. code-block:: python

    >>> from sbpy.photometry import HG
    >>>
    >>> rh = [1, 2, 4] * u.au
    >>> delta = [1, 2, 3] * u.au
    >>> phase = [0, 10, 20] * u.deg
    >>> Phi = lambda phase: 10**(-0.4 * HG(0, 0.12)(phase))
    >>> 
    >>> print(scale.geometry(rh, delta, phase, Phi=Phi))  # pytest: +FLOAT_CMP
    [0.         3.69335624 6.43548318] mag


Considerations for comets
-------------------------

Comets are extended objects, and scaling by geometry may be interpreted different ways.  Does one want to account for the variation of activity with heliocentric distance?  Or differential losses from the photometric aperture?  These goals are accounted for with the ``activity_slope`` and ``delta_slope`` keyword arguments.

Assuming photometry of a cometary coma measured within fixed angular apertures, and activity that scales with :math:`r_\mathrm{h}^-4`, get the scale factors for the same geometry as above:

.. code-block:: python

    >>> from sbpy.activity import phase_HalleyMarcus
    >>>
    >>> s = scale.geometry(
    ...     rh,
    ...     delta,
    ...     phase,
    ...     activity_slope=-4,
    ...     delta_slope=-1,
    ...     Phi=phase_HalleyMarcus
    ... )
    >>> print(s)
    [ 0.          5.67547505 10.95010407] mag


Activity scaling
================

Scale factors for activity can be calculated independently from the geometrical factors using :func:`lsstsso.scale.activity`.  The parameters are heliocentric distance, observer-target distance, heliocentric distance power-law slope, and observer-target distance power-law slope.

Assuming photometry of a cometary coma measured within fixed angular apertures, and activity that scales with :math:`r_\mathrm{h}^-4`, get the activity scale factors:

.. code-block:: python

    >>> import astropy.units as u
    >>> from lsstsso import scale
    >>>
    >>> rh = [1, 2, 4] * u.au
    >>> delta = [1, 2, 3]  * u.au
    >>> activity_slope = -4
    >>> delta_slope = -1  # for fixed-angular photometry of a coma
    >>>
    >>> print(scale.activity(rh, delta, activity_slope, delta_slope))
    [0.         3.76287495 7.21340305] mag


Color scaling
=============

From a collection of photometry, calculate the scale factors to transform the observations into a common bandpass.

Calculate the scale factors to transform u- and g-band photometry to r-band photometry:

.. code-block:: python

    >>> import astropy.units as u
    >>> from lsstsso import scale
    >>>
    >>> m = [1, 2, 4] * u.mag
    >>> unc = [0.01, 0.01, 0.01] * u.mag
    >>> bands = ["r", "g", "u"]
    >>>
    >>> s, s_unc = scale.color(m, unc, bands, "r")
    >>> print(s)
    [ 0. -1. -3.] mag
    >>> print(s_unc)
    [0.         0.01414214 0.02      ] mag

.. attention::

    :func:`lsstsso.scale.color` does not yet account for correlations between color measurements.
