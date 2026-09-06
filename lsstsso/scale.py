from typing import Callable
import astropy.units as u
import numpy as np
from sbpy.activity import phase_HalleyMarcus

from .band import Band


def activity(
    rh: u.Quantity[u.physical.length],
    delta: u.Quantity[u.physical.length],
    rh_slope: float,
    delta_slope: float,
) -> u.Quantity[u.mag]:
    """Scale factor (mag) accounting for activity.

    Use this scale factor to transform absolute magnitude into cometary absolute
    magnitude, Hy.


    Parameters
    ----------
    rh : Quantity
        Heliocentric distance.

    delta : Quantity
        Topocentric distance.

    rh_slope : float
        Scale by rh**rh_slope.

    delta_slope : float
        -1 for comets with a 1/rho coma, measured with fixed angular aperture
        photometry.


    Returns
    -------
    scale : Quantity
        Scale factor in magnitudes.

    """

    return -2.5 * np.log10(
        ((1 * u.au) / rh) ** rh_slope * ((1 * u.au) / delta) ** delta_slope
    )


def color(
    m: u.Quantity[u.mag],
    unc: u.Quantity[u.mag],
    bands: np.ndarray[Band],
    anchor: Band | str = Band.r,
):
    """Scale factor (mag) accounting for color.

    The scale factors scale ``m`` to the color of ``anchor``.


    Parameters
    ----------
    m : Quantity
        Apparent magnitudes.

    unc : Quantity
        Uncertainties on ``m``.

    bands : array of Band
        The observational bands for each ``m``.

    anchor : Band or str
        The band to anchor to.


    Returns
    -------
    scale : dict
        Scale factor to match the anchor bandpass in magnitudes.

    """

    if isinstance(anchor, str):
        anchor = Band[anchor]

    if anchor not in bands:
        raise ValueError(f"Cannot estimate color for band {anchor}")

    m = u.Quantity(m, u.mag)
    unc = u.Quantity(unc, u.mag)

    # averaged apparent magnitude
    avg = {}
    avg_unc = {}
    for band in set(bands):
        # find all observations in this band
        i = bands == band

        # average them together
        avg[band], avg_unc[band] = weighted_mean(m[i], unc[i])

    # calculate colors
    color = {}
    color_unc = {}
    for band in Band:
        if band == anchor:
            color[band] = 0
            color_unc[band] = 0
            continue

        if band not in bands:
            color[band] = np.ma.masked
            color_unc[band] = np.ma.masked
            continue

        color[band] = float(avg[anchor] - avg[band])
        color_unc[band] = float(np.hypot(avg_unc[band], avg_unc[anchor]))

    return color, color_unc


def geometry(
    rh: u.Quantity[u.physical.length],
    delta: u.Quantity[u.physical.length],
    phase: u.Quantity[u.physical.angle],
    Phi: Callable = phase_HalleyMarcus,
):
    """Scale factor (mag) accounting for geometry.

    Use this scale factor to transform apparent magnitude to absolute magnitude.


    Parameters
    ----------
    rh : Quantity
        Heliocentric distance.

    delta : Quantity
        Topocentric distance.

    phase : Quantity
        Phase angle.

    Phi : callable
        Linear phase function.


    Returns
    -------
    scale : array
        Scale factor in magnitudes.

    """

    return -5 * np.log10(rh * delta / u.au**2) + 2.5 * (Phi(phase) / Phi(0))


def weighted_mean(x, unc):
    i = np.isfinite(x * unc)
    if i.sum() == 0:
        return np.nan, np.nan
    m, sw = np.average(x[i], weights=unc[i] ** -2, returned=True)
    return m, sw**-0.5
