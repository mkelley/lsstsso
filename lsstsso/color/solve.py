"""Tools to make a consistent color matrix."""

from itertools import combinations

import numpy as np
from scipy.optimize import curve_fit

from ..band import Band
from .color import Color
from .color_matrix import ColorMatrix


def _to_index(i, j):
    """Convert matrix indices to index of flattened upper triangle."""
    return int(11 / 2 * i - i**2 / 2 - 1) + j - i


def _from_index(k):
    """Convert flattened upper triangle index to matrix indices.

    [  0    1    2    3    4    5    6    7    8    9   10   11   12   13   14]
    [u-g, u-r, u-i, u-z, u-y, g-r, g-i, g-z, g-y, r-i, r-z, r-y, i-z, i-y, z-y]
    """

    return [
        (0, 1),
        (0, 2),
        (0, 3),
        (0, 4),
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
        (2, 3),
        (2, 4),
        (2, 5),
        (3, 4),
        (3, 5),
        (4, 5),
    ][k]


def solve(cm: ColorMatrix) -> ColorMatrix:
    """New color solution with least-squares approach.

    The colors will be adjusted and empty colors filled to make a consistent
    color matrix.  The fitter will attempt to minimize the color matrix's
    chi-sq.


    Parameters
    ----------
    cm : ColorMatrix
        The color matrix to solve.


    Returns
    -------
    result : ColorMatrix

    """

    # there may be up to 75 equations
    A = np.zeros((75, 15))
    b = np.zeros((75,))
    unc = np.ones((75,))

    bands = list(Band)

    # track the equation we are on
    eqn = 0

    # the first equations are trivial
    print("Equations:")
    for vars, j in combinations(range(6), 2):
        if cm.index[vars, j] is not np.ma.masked:
            A[eqn, _to_index(vars, j)] = 1
            b[eqn] = cm.index[vars, j]
            unc[eqn] = cm.unc[vars, j]
            eqn += 1
            print(f"  {bands[vars]}-{bands[j]} = {cm.index[vars, j]}")

    # the next equations are two color combinations
    for i, j, k in combinations(range(6), 3):
        n = (
            int(cm.index[i, j] is not np.ma.masked)
            + int(cm.index[i, k] is not np.ma.masked)
            + int(cm.index[j, k] is not np.ma.masked)
        )
        if n < 2:
            continue

        if cm.index[i, j] is not np.ma.masked:
            A[eqn, [_to_index(i, k), _to_index(j, k)]] = [1, -1]
            b[eqn] = cm.index[i, j]
            unc[eqn] = cm.unc[i, j]
            eqn += 1
            print(
                f"  {bands[i]}-{bands[k]} - ({bands[j]}-{bands[k]}) = {bands[i]}-{bands[j]}"
            )

        if cm.index[i, k] is not np.ma.masked:
            A[eqn, [_to_index(i, j), _to_index(j, k)]] = [1, 1]
            b[eqn] = cm.index[i, k]
            unc[eqn] = cm.unc[i, k]
            eqn += 1
            print(
                f"  {bands[i]}-{bands[j]} + {bands[j]}-{bands[k]} = {bands[i]}-{bands[k]}"
            )

        if cm.index[j, k] is not np.ma.masked:
            A[eqn, [_to_index(i, j), _to_index(i, k)]] = [-1, 1]
            b[eqn] = cm.index[j, k]
            unc[eqn] = cm.unc[j, k]
            print(
                f"  -({bands[i]}-{bands[j]}) + {bands[i]}-{bands[k]} = {bands[j]}-{bands[k]}"
            )

    # least squares fit

    def model(A, *x):
        return A @ np.array(x)

    guess = np.array(
        [
            1.83,
            2.42,
            2.63,
            2.68,
            2.71,
            0.59,
            0.8,
            0.85,
            0.88,
            0.21,
            0.26,
            0.29,
            0.05,
            0.08,
            0.03,
        ]
    )

    # remove unused equations
    A = A[:eqn]
    b = b[:eqn]
    unc = unc[:eqn]

    # remove unused variables
    vars = np.flatnonzero(np.sum(A**2, 0))
    A = A[:, vars]
    guess = guess[vars]

    fit, cov = curve_fit(
        model,
        A,
        b,
        p0=guess,
        sigma=unc,
        absolute_sigma=True,
        method="trf",
    )
    fit_unc = np.sqrt(np.diag(cov))

    print("\nSolution:")
    colors = []
    for k, index in enumerate(vars):
        vars, j = _from_index(index)
        colors.append(Color(bands[vars], bands[j], fit[k], fit_unc[k]))
        print(f"  {colors[-1]}")

    return ColorMatrix(colors)
