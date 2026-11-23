from itertools import combinations

import numpy as np

from ..band import Band
from .color_matrix import ColorMatrix


def sample(cm: ColorMatrix, bands: list[Band]) -> list[ColorMatrix]:
    """Sample specific bands from a ColorMatrix.

    Get a new ColorMatrix that only has colors sharing bands in a requested
    list.


    Parameters
    ----------
    cm : ColorMatrix
        The color matrix to sample.

    bands : list of Band
        Any colors with these bands are returned, e.g., ``bands=["g", "r"]``
        will return ``g-r``, but not ``u-g``.


    Results
    -------
    sampled : ColorMatrix
        The requested colors.

    """

    sampled = ColorMatrix()

    ii = []  # the color indices to get
    bands = sorted([Band(b) for b in bands])
    for blue, red in combinations(bands, 2):
        i = ColorMatrix.bands_to_array_index(blue, red)
        if cm.index[i] is not np.ma.masked:
            ii.append(i)

    sampled.index[ii] = cm.index[ii]

    # use numpy indexing tricks to just get the covariance rows and columns we
    # need
    i = np.ix_(ii, ii)
    sampled.cov[i] = cm.cov[i]

    return sampled
