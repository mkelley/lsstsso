"""Tools to fit a set of colors."""

from itertools import combinations

import numpy as np
from scipy.special import factorial

from .color import Color
from .color_matrix import ColorMatrix


def solve(colors: list[Color]) -> ColorMatrix:
    """Solve for a new color solution with a least-squares approach.

    The colors will be adjusted and all possible band combinations calculated to
    make a consistent color matrix.  The fitter will attempt to minimize the
    color matrix's chi-square.  This may result in correlated uncertainties for
    some measurements.


    Parameters
    ----------
    colors : list of Color
        A list of the colors to solve.


    Returns
    -------
    result : ColorMatrix
        The new color set.

    cov : numpy.ndarray
        The fit covariance matrix.

    cov_colors : list of tuples
        The row and columns of ``cov`` correspond to the color pairs in this
        list, e.g., ``cov[i, j]`` is the co-variance between ``cov_colors[i]``
        and ``cov_colors[j]``.


    Examples
    --------

    From an observation of :math:`u-g` and :math:`u-r`, calculate :math:`g-r`:

    >>> from lsstsso.color import Color, solve
    >>>
    >>> colors = [Color("u", "g", 1.0, 0.1), Color("u", "r", 1.4, 0.1)]
    >>> cm, _, _ = solve(colors)
    >>> print(cm)
    u-g = 1.000 ± 0.100 mag
    u-r = 1.400 ± 0.100 mag
    g-r = 0.400 ± 0.141 mag

    """

    cm = ColorMatrix(colors)

    # There are 5 fundamental colors: u-g, g-r, r-i, i-z, z-y.  But observations
    # can be of any band pair, e.g., g-i.  This gives us 5 variables, and 6! /
    # (2! * (6 - 2)!) = 15 equations. The variables are the observed magnitudes
    # relative to u.  Let u = 0.  The equations are the 15 colors.

    # How many bands are given?
    bands = sorted({color.left for color in colors} | {color.right for color in colors})
    n_bands = len(bands)
    n_colors = int(factorial(n_bands) / (2 * factorial(n_bands - 2)))

    # A is a set of equations for each color.  The columns are the brightness
    # measurements, except for the shortest wavelength, which is implicitly 0
    # for every row.  For example, if the bands are u, g, r, then the color u-g
    # = [-1, 0], and u-r = [0, -1].  For g-r, the equation is [1, -1].
    A = np.zeros((n_colors, n_bands - 1))

    # b is the observed color
    b = np.zeros(len(cm))

    # u is the uncertainty
    u = np.zeros(len(cm))

    # generate the equation array and track which row is which color
    equations = {}
    for i, (j, k) in enumerate(combinations(range(n_bands), 2)):
        equations[(j, k)] = i

        if j != 0:
            A[i, j - 1] = 1

        A[i, k - 1] = -1

    # make the solution array from our observations
    eqn = []
    for i, color in enumerate(cm):
        j = bands.index(color.left)
        k = bands.index(color.right)
        eqn.append(equations[(j, k)])

        b[i] = color.index.value
        u[i] = color.unc.value

    # get the equations to solve and weight them by 1 / measurement uncertainty
    W = np.diag(1 / u)
    wA_obs = W @ A[eqn]
    wb = W @ b

    # solve!
    A_hat, _, _, _ = np.linalg.lstsq(wA_obs, wb, rcond=1e-7)
    cov_A = np.linalg.inv(wA_obs.T @ wA_obs)

    # get all colors and uncertainties
    colors = A @ A_hat
    cov = A @ cov_A @ A.T
    unc = np.sqrt(np.diag(cov))

    colors = [
        Color(bands[i], bands[j], colors[k], unc[k]) for (i, j), k in equations.items()
    ]
    cm = ColorMatrix(colors)

    # return the covariance and the corresponding colors
    cov_colors = [(str(bands[i]), str(bands[j])) for i, j in equations]

    return ColorMatrix(colors), cov, cov_colors
