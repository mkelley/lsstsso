from itertools import combinations, pairwise

import astropy.units as u
import numpy as np

from ..band import Band
from ..util import weighted_mean
from .color_matrix import ColorMatrix


def measure(
    m: u.Quantity[u.mag],
    unc: u.Quantity[u.mag],
    bands: np.ndarray[Band],
    all: bool = False,
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

    all : bool, optional
        By default, the minimum color set is computed.  For example, if
        observations in u, r, and i are provided, only u-r, and r-i are
        returned, not u-i.  Set ``all=True`` to return all color pairings.


    Returns
    -------
    result : ColorMatrix
        Measured colors.

    """

    m = u.Quantity(m, u.mag).to_value("mag")
    unc = u.Quantity(unc, u.mag).to_value("mag")
    bands = np.array(bands)

    if len(set(bands)) < 2:
        return ColorMatrix()

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

    if not all:
        # if we have u, g, r: just want u-g, g-r
        # if we have u, r, i: just want u-r, r-i
        # if we have u, g, r, i: just want u-g, g-r, r-i
        wanted = list(pairwise(sorted(Band(b) for b in set(bands))))
        for i, (blue, red) in enumerate(combinations(Band, 2)):
            if (blue, red) not in wanted:
                A[i] = 0

    # calculate
    mask = (A != 0) @ avg.mask + (np.prod(A == 0, 1) == 1)
    index = np.ma.MaskedArray(A @ avg.filled(0), mask=mask)

    cov_mask = np.zeros((15, 15), bool)
    cov_mask[mask] = True
    cov_mask[:, mask] = True
    cov = np.ma.MaskedArray(
        A @ np.diag(avg_unc.filled(1) ** 2) @ A.T,
        mask=cov_mask,
    )

    return ColorMatrix(index, cov)
