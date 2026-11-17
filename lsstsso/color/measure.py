from itertools import pairwise

import astropy.units as u
import numpy as np

from ..band import Band
from ..util import weighted_mean
from .color import Color


def measure(
    m: u.Quantity[u.mag],
    unc: u.Quantity[u.mag],
    bands: np.ndarray[Band],
    anchor: Band | str | None = None,
) -> list[Color]:
    """Calculate colors from observations.


    Parameters
    ----------
    m : Quantity
        Apparent magnitudes.

    unc : Quantity
        Uncertainties on ``m``.

    bands : array of Band
        The observational bands for each ``m``.

    anchor : Band or str, optional
        Measure with respect to this band.


    Returns
    -------
    colors: list of Color
        Measured colors.

    """

    m = u.Quantity(m, u.mag)
    unc = u.Quantity(unc, u.mag)

    # averaged apparent magnitude
    avg = {}
    avg_unc = {}
    for band in set(bands):
        # find all observations in this band
        i = np.array(bands) == band

        # average them together
        avg[band], avg_unc[band] = weighted_mean(m[i], unc[i])

    # setup color pairs
    if anchor is None:
        pairs = pairwise(sorted({Band(b) for b in bands}))
    else:
        anchor = Band(anchor)
        pairs = [(band, anchor) for band in bands if band != anchor]

    # calculate colors
    colors = []
    for left, right in pairs:
        colors.append(
            Color(
                left,
                right,
                avg[left] - avg[right],
                np.hypot(avg_unc[left], avg_unc[right]),
            )
        )

    return colors
