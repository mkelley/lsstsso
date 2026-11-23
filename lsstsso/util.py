"""Generic methods for ``lsstsso`` functionality."""

from itertools import combinations

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


def merge_sets(sets: list[set]) -> list[set]:
    """Merge overlapping sets.


    Parameters
    ----------
    sets : list of set
        The sets to merge.


    Returns
    -------
    merged : list of set
        The merged sets.


    Examples
    --------

    >>> from lsstsso.util import merge_sets
    >>>
    >>> sets = [{1, 2}, {2, 3}, {5, 6}]
    >>> merged = merge_sets(sets)
    >>> print(merged)
    [{1, 2, 3}, {5, 6}]

    """

    done = []
    merged = []
    for bands1, bands2 in combinations(sets, 2):
        if bands1 in done or bands2 in done:
            continue

        if not bands1.isdisjoint(bands2):
            done.extend((bands1, bands2))
            merged.append(bands1 | bands2)

    # anything not merged? append it
    for bands in sets:
        if bands not in done:
            merged.append(bands)

    if len(merged) == len(sets):
        return merged
    else:
        return merge_sets(merged)
