from itertools import combinations

import astropy.units as u
import numpy as np

from ..band import Band
from ..util import weighted_mean
from .color_matrix import ColorMatrix


def measure(
    m: u.Quantity[u.mag],
    unc: u.Quantity[u.mag],
    bands: np.ndarray[Band],
) -> ColorMatrix:
    """Calculate colors from observations.


    Parameters
    ----------
    m : Quantity
        Apparent magnitudes.

    unc : Quantity
        Uncertainties on ``m``.

    bands : array of Band
        The observational bands for each ``m``.


    Returns
    -------
    result : ColorMatrix
        Measured colors.

    """

    m = u.Quantity(m, u.mag).to_value("mag")
    unc = u.Quantity(unc, u.mag).to_value("mag")
    bands = np.array(bands)

    # averaged apparent magnitude
    avg, avg_unc = np.ma.zeros((2, 6))
    avg.mask = [True] * 6
    avg_unc.mask = [True] * 6
    for i, band in enumerate(Band):
        # find all observations in this band
        j = bands == band

        if not any(j):
            continue

        # average them together
        avg[i], avg_unc[i] = weighted_mean(m[j], unc[j])

    # color equations: u-g, u-r, etc
    A = np.zeros((15, 6), int)
    for i, (j, k) in enumerate(combinations(range(6), 2)):
        A[i, j] = 1
        A[i, k] = -1

    # calculate
    mask = ((A != 0) @ avg.mask) != 0
    index = np.ma.MaskedArray(A @ avg.filled(1), mask=mask)

    cov_mask = np.zeros((15, 15), bool)
    cov_mask[mask] = True
    cov_mask[:, mask] = True
    cov = np.ma.MaskedArray(
        A @ np.diag(avg_unc.filled(1) ** 2) @ A.T,
        mask=cov_mask,
    )

    return ColorMatrix(index, cov)
