from collections.abc import Callable
from warnings import warn

import astropy.units as u
import numpy as np
from sbpy.activity import phase_HalleyMarcus

from .band import Band
from .color.measure import measure
from .color.solve import solve


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
        -1 is recommended for comets with a 1/rho coma, measured with fixed
        angular aperture photometry.  -2 is recommended for comets measured with
        fixed linear aperture.


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
    anchor: Band | str,
) -> tuple[u.Quantity, u.Quantity]:
    """Scale factor (mag) accounting for color.


    Parameters
    ----------
    m : |Quantity|
        Apparent magnitudes.

    unc : |Quantity|
        Uncertainties on ``m``.

    bands : array of |Band|
        The observational bands for each ``m``.

    anchor : |Band| or str
        Scale to this band.


    Returns
    -------
    scale, scale_unc : |Quantity|
        The scale factors and uncertainties.

    """

    warn("lsstsso.scale.color does not yet account for correlations between colors.")

    cm, _, _ = solve(measure(m, unc, bands))
    scale = np.zeros_like(m)
    scale_unc = np.zeros_like(unc)
    bands = np.array(bands)
    for band in set(bands):
        i = bands == band
        scale[i], scale_unc[i] = cm.transform(0 * u.mag, 0 * u.mag, band, anchor)

    return scale, scale_unc


def geometry(
    rh: u.Quantity[u.physical.length],
    delta: u.Quantity[u.physical.length],
    phase: u.Quantity[u.physical.angle],
    activity_slope: float = 0,
    delta_slope: float = -1,
    Phi: Callable = phase_HalleyMarcus,
) -> u.Quantity[u.mag]:
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

    activity_slope : int or float
        Power-law slope for activity scale factor with rh.

    delta_slope : int or float
        Power-law slope for delta, e.g., -1 recommended for comae measured with
        fixed angular apertures, or -2 recommended for comae measured with fixed
        linear apertures.  -2 for nuclei.

    Phi : callable
        Linear phase function.


    Returns
    -------
    scale : array
        Scale factor in magnitudes.

    """

    return (
        (-5 + 2.5 * activity_slope) * np.log10(rh / u.au)
        + 2.5 * delta_slope * np.log10(delta / u.au)
        + 2.5 * np.log10(Phi(phase) / Phi(0 * u.deg))
    )
