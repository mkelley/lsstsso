"""Generic methods for ``lsstsso`` functionality."""

import astropy.units as u
import numpy as np


def weighted_mean(
    x: np.ndarray | u.Quantity, unc: np.ndarray | u.Quantity
) -> tuple[np.ndarray | u.Quantity, np.ndarray | u.Quantity]:
    """Calculate weighted mean and uncertainty.


    Parameters
    ----------
    x : |ndarray| or |Quantity|
        Measurements.

    unc : |ndarray| or |Quantity|
        Measurement uncertainties.


    Returns
    -------
    wm, wm_unc : |ndarray| or |Quantity|
        Weighted mean and uncertainty, or NaN if they cannot be calculated.

    """

    i = np.isfinite(x * unc)

    if i.sum() == 0:
        return np.nan, np.nan

    m, sw = np.average(x[i], weights=unc[i] ** -2, returned=True)
    return m, sw**-0.5
