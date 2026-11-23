"""Tools to fit a set of colors."""

from itertools import combinations

import numpy as np
from scipy.special import factorial

from ..util import merge_sets
from .color_matrix import ColorMatrix
from .merge import merge
from .sample import sample


def solve(*color_matrices: list[ColorMatrix]) -> ColorMatrix:
    """Solve for a new color solution with a least-squares approach.

    The colors will be adjusted and all possible band combinations calculated to
    make a consistent color matrix.  The fitter will attempt to minimize the
    color matrix's chi-square.  This may result in correlated uncertainties for
    some measurements.


    Parameters
    ----------
    color_matrices : array of ColorMatrix
        The input colors.  Multiple color matrices may be given.


    Returns
    -------
    result : ColorMatrix
        The new color set.


    Examples
    --------

    From an observation of `u-g` and `u-r`, calculate `g-r`:

    >>> from lsstsso.color import Color, solve
    >>>
    >>> cm = ColorMatrix.from_colors(
    ...     [
    ...         Color("u", "g", 1.0, 0.1),
    ...         Color("u", "r", 1.4, 0.1)
    ...     ]
    ... )
    >>> updated = solve(cm)
    >>> print(updated)
    u-g = 1.000 ± 0.100 mag
    u-r = 1.400 ± 0.100 mag
    g-r = 0.400 ± 0.141 mag

    """

    # There are 5 fundamental colors: u-g, g-r, r-i, i-z, z-y.  But observations
    # can be of any band pair, e.g., g-i.  This gives us 5 variables, and 6! /
    # (2! * (6 - 2)!) = 15 equations.

    # first, collect all the colors
    color_sets = []
    for cm in color_matrices:
        for color in cm:
            pair = {color.left, color.right}
            if pair not in color_sets:
                color_sets.append(pair)

    # identify disjoint color sets
    band_sets = merge_sets(color_sets)

    # if there are multiple band sets, then split the color matrices into the
    # independent sets and solve each, then merge the results
    if len(band_sets) > 1:
        results = []  # collect all the solutions
        for bands in band_sets:
            split = [sample(cm, bands) for cm in color_matrices]
            results.append(solve(*split))

        # merge and return the results
        return merge(results)

    # How many bands are given?  For the method below, we need to limit
    # calculations to the observed bands.
    bands = set()
    for cm in color_matrices:
        for color in cm:
            bands |= {color.left, color.right}

    bands = sorted(bands)
    n_bands = len(bands)
    n_obs = sum([len(cm) for cm in color_matrices])
    n_colors = int(factorial(n_bands) / (2 * factorial(n_bands - 2)))

    # A maps colors to observations (A[obs, color]), b is the observation
    # vector, C is the covariance matrix
    A = np.zeros((n_obs, n_bands - 1))
    b = np.zeros(n_obs)
    C = np.zeros((n_obs, n_obs))
    obs = 0  # track the observation index
    for cm in color_matrices:
        ii = []  # track the ColorMatrix indices
        for i, color in enumerate(cm):
            j = bands.index(color.left)
            k = bands.index(color.right)

            # this color is the sum of all colors from j to k, i.e., u-r = u-g + g-r
            A[obs + i, j:k] = 1

            ii.append(cm.bands_to_array_index(color.left, color.right))

        b[obs : obs + len(ii)] = cm.index[ii]
        C[obs : obs + len(ii), obs : obs + len(ii)] = cm.cov[ii][:, ii].filled(0)
        obs += len(cm)

    # solve generalized least squares (A^T @ C^-1 @ A) x = A^T @ C^-1 @ y, where
    # C is the covariance matrix, x is the solution and y are the observations

    # get C^-1 @ A by solving the equation C @ (C^-1 @ A) = A
    Cinv_A = np.linalg.solve(C, A)  # C^-1 @ A

    X = A.T @ Cinv_A  # A^T @ C^-1 @ A
    Y = Cinv_A.T @ b  # A^T @ C^-1 @ y

    # now, solve the GLS equation (avoid using np.linalg.inv)
    x_hat = np.linalg.solve(X, Y)
    cov_x_hat = np.linalg.solve(X, np.identity(X.shape[0]))

    # project result onto all colors
    D = np.zeros((n_colors, n_bands - 1))
    for i, (j, k) in enumerate(combinations(range(n_bands), 2)):
        D[i, j:k] = 1

    y_all = D @ x_hat
    cov_all = D @ cov_x_hat @ D.T

    # make and return the result color matrix
    result = ColorMatrix()

    ii = []
    for i, (blue, red) in enumerate(combinations(bands, 2)):
        ii.append(ColorMatrix.bands_to_array_index(blue, red))

    result.index[ii] = y_all
    for i in range(n_colors):
        for j in range(n_colors):
            result.cov[ii[i], ii[j]] = cov_all[i, j]

    return result
