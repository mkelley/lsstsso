from collections.abc import Callable

import astropy.units as u
import numpy as np


def activity(
    rh: u.Quantity[u.physical.length],
    delta: u.Quantity[u.physical.length],
    rh_slope: float,
    delta_slope: float,
) -> u.Quantity[u.mag]:
    """Scale factor (mag) accounting for activity.

    Use this scale factor to, e.g., scale between cometary absolute magnitude,
    :math:`H_y`, and absolute magnitude, `H`: :math:`H = H_y + scale`.


    Parameters
    ----------
    rh : Quantity
        Heliocentric distance.

    delta : Quantity
        Topocentric distance.

    rh_slope : float
        Scale by rh**rh_slope.

    delta_slope : float
        -1 is recommended for comets with a 1/rho coma, measured with
        fixed-angular aperture photometry.  -2 is recommended for comets
        measured with fixed-linear apertures.


    Returns
    -------
    scale : Quantity
        Scale factor in magnitudes.

    """

    return (
        2.5
        * np.log10(((1 * u.au) / rh) ** rh_slope * ((1 * u.au) / delta) ** delta_slope)
        * u.mag
    )


def geometry(
    rh: u.Quantity[u.physical.length],
    delta: u.Quantity[u.physical.length],
    phase: u.Quantity[u.physical.angle] | None = None,
    activity_slope: float = 0,
    delta_slope: float = -2,
    Phi: Callable | None = None,
) -> u.Quantity[u.mag]:
    """Scale factor (mag) accounting for geometry.

    Use this scale factor to transform between absolute and apparent magnitude.


    Parameters
    ----------
    rh : Quantity
        Heliocentric distance.

    delta : Quantity
        Topocentric distance.

    phase : Quantity, optional
        Phase angle.

    activity_slope : int or float, optional
        Power-law slope for activity scale factor with rh.

    delta_slope : int or float, optional
        Power-law slope for delta, e.g., -1 recommended for comae measured with
        fixed angular apertures, or -2 recommended for comae measured with fixed
        linear apertures.  -2 for nuclei.

    Phi : callable, optional
        Also correct for phase effect with this linear phase function.


    Returns
    -------
    scale : array
        Scale factor in magnitudes to convert absolute to apparent brightness:
        :math:`m = H + scale`.

    """

    scale = (5 - 2.5 * activity_slope) * np.log10(
        rh / u.au
    ) - 2.5 * delta_slope * np.log10(delta / u.au)

    if None not in [phase, Phi]:
        scale -= 2.5 * np.log10(Phi(phase) / Phi(0 * u.deg))

    return scale * u.mag
