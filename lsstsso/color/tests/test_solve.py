import numpy as np
from numpy.linalg import norm

from ..color import Color
from ..color_matrix import ColorMatrix
from ..solve import solve


def test_solve_simple():
    """Only one way to calculate the missing color"""

    colors = [
        Color("u", "r", 2.0, 0.06),
        Color("g", "r", 0.5, 0.013),
    ]

    cm = ColorMatrix(colors)
    result, cov, cov_colors = solve(colors)

    assert np.isclose(result["u", "g"].index.value, 1.5)
    assert np.isclose(result["u", "g"].unc.value, np.hypot(0.06, 0.013))

    # no other colors should have been filled
    assert np.sum(result.index.mask) == (np.sum(cm.index.mask) - 2)

    assert cov_colors == [("u", "g"), ("u", "r"), ("g", "r")]

    assert np.isclose(cov[0, 0], 0.06**2 + 0.013**2)  # var(u-g)
    assert np.isclose(cov[1, 1], 0.06**2)  # var(u-r)
    assert np.isclose(cov[2, 2], 0.013**2)  # var(g-r)

    assert np.isclose(cov[0, 1], 0.06**2)  # cov(u-g, u-r)
    assert np.isclose(cov[0, 2], -(0.013**2))  # cov(u-g, g-r)
    assert np.isclose(cov[1, 2], 0)  # cov(u-r, g-r)


def test_solve_multiple():
    """Two ways to calculate the missing color"""

    # solar colors from Willmer 2018
    colors = [
        Color("u", "g", 1.21, 0.01),
        Color("u", "r", 1.63, 0.01),
        Color("g", "i", 0.54, 0.01),
        Color("r", "i", 0.12, 0.01),
    ]

    cm = ColorMatrix(colors)
    result, cov, cov_colors = solve(colors)

    # There were two ways to calculate u-i and g-r, e.g., u-i = u-g + g-i and
    # u-i = u-r + r-i.  The uncertainty on each is 0.01 * sqrt(2).  Combining
    # the two yields an uncertainty of 0.01.
    assert np.isclose(result["u", "i"].index.value, 1.75)
    assert np.isclose(result["u", "i"].unc.value, 0.01)

    assert np.isclose(result["g", "r"].index.value, 0.42)
    assert np.isclose(result["g", "r"].unc.value, 0.01)

    # the others should be the same, except the uncertainties will be smaller by
    # sqrt(3) / 2
    for color in cm:
        k = (color.left, color.right)
        assert np.isclose(result[k].index.value, color.index.value)
        assert np.isclose(result[k].unc.value, color.unc.value * np.sqrt(3) / 2)

    # no other colors should have been filled
    assert np.sum(result.index.mask) == (np.sum(cm.index.mask) - 4)

    assert cov_colors == [
        ("u", "g"),
        ("u", "r"),
        ("u", "i"),
        ("g", "r"),
        ("g", "i"),
        ("r", "i"),
    ]

    # there is now explicit correlation between the observed colors given that:
    #   u-g - (u-r) + g-i - (r-i) = 0
    assert np.isclose(cov[0, 0], 7.5e-5)  # var(u-g)
    assert np.isclose(cov[0, 1], 2.5e-5)  # cov(u-g, u-r)
    assert np.isclose(cov[0, 4], -2.5e-5)  # cov(u-g, g-i)
    assert np.isclose(cov[0, 5], 2.5e-5)  # cov(u-g, r-i)


def test_solve_two_steps():
    """In this test, u-g is the combination of three other colors:

    u-g = u-z - (i-z) - (g-i)

    """

    # solar colors from Willmer 2018
    colors = [
        Color("u", "z", 1.76, 0.01),
        Color("g", "i", 0.54, 0.01),
        Color("i", "z", 0.01, 0.01),
    ]

    cm = ColorMatrix(colors)
    assert cm["u", "i"] is np.ma.masked
    assert cm["u", "g"] is np.ma.masked

    result, _, _ = solve(cm)
    assert np.isclose(result["u", "i"].index.value, 1.75)
    assert np.isclose(result["u", "g"].index.value, 1.21)

    assert np.isclose(result["u", "i"].unc.value, np.sqrt(2) * 0.01)
    assert np.isclose(result["u", "g"].unc.value, np.sqrt(3) * 0.01)
