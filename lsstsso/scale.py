import astropy.units as u
import numpy as np
from sbpy.activity import phase_HalleyMarcus

from .band import Band


def color_scales(m, unc, bands, anchor: Band | str = Band.r):
    """Scale factor (mag) accounting for color.

    The scale factors scale ``m`` to the color of ``anchor``.


    Parameters
    ----------
    m : array
        Apparent magnitudes, already scaled for variations in geometry.

    unc : array
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

    # time averaged apparent magnitude corrected by gemetrical circumstances
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


def scale_by_geometry(
    rh,
    delta,
    phase,
    rh_slope=-4,
    delta_slope=-1,
    Phi=phase_HalleyMarcus,
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

    rh_slope : float
        Scale by rh**rh_slope.

    delta_slope : float
        Scale by delta**delta_slope.  Usually -1 for comets with fixed angular
        aperture photometry, -2 any other photometry.

    Phi : callable
        Phase function.


    Returns
    -------
    scale : array
        Scale factor in magnitudes.

    """

    return (
        -2.5
        * np.log10(((1 * u.au) / rh) ** rh_slope * ((1 * u.au) / delta) ** delta_slope)
        + Phi(0)
        - Phi(phase)
    )


def weighted_mean(x, unc):
    i = np.isfinite(x * unc)
    if i.sum() == 0:
        return np.nan, np.nan
    m, sw = np.average(x[i], weights=unc[i] ** -2, returned=True)
    return m, sw**-0.5
