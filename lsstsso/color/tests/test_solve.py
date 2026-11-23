import numpy as np

from ..color import Color
from ..color_matrix import ColorMatrix
from ..solve import solve


def test_solve_trivial():
    """Nothing to calculate"""

    colors = [
        Color("u", "r", 2.0, 0.06),
    ]

    cm = ColorMatrix.from_colors(colors)
    result = solve(cm)

    assert len(result) == 1
    assert np.isclose(cm.index[1], 2)

    expected = np.ma.zeros((15, 15))
    expected.mask = True
    expected[1, 1] = 0.06**2
    assert np.ma.allclose(result.cov, expected)


def test_solve_simple():
    """Only one way to calculate the missing color"""

    colors = [
        Color("u", "r", 2.0, 0.06),
        Color("g", "r", 0.5, 0.013),
    ]

    cm = ColorMatrix.from_colors(colors)
    result = solve(cm)

    assert np.isclose(result["u", "g"].index.value, 1.5)
    assert np.isclose(result["u", "r"].index.value, 2.0)
    assert np.isclose(result["g", "r"].index.value, 0.5)

    # only one color difference:
    assert np.sum(result.index.mask) == (np.sum(cm.index.mask) - 1)

    # check variances
    assert np.isclose(result.cov[0, 0], 0.06**2 + 0.013**2)  # var(u-g)
    assert np.isclose(result.cov[1, 1], 0.06**2)  # var(u-r)
    assert np.isclose(result.cov[5, 5], 0.013**2)  # var(g-r)

    # check covariances
    assert np.isclose(result.cov[0, 1], 0.06**2)  # cov(u-g, u-r)
    assert np.isclose(result.cov[0, 5], -(0.013**2))  # cov(u-g, g-r)
    assert np.isclose(result.cov[1, 5], 0)  # cov(u-r, g-r)


def test_solve_multiple():
    """Two ways to calculate the missing color"""

    # solar colors from Willmer 2018
    colors = [
        Color("u", "g", 1.21, 0.01),
        Color("u", "r", 1.63, 0.01),
        Color("g", "i", 0.54, 0.01),
        Color("r", "i", 0.12, 0.01),
    ]

    cm = ColorMatrix.from_colors(colors)
    result = solve(cm)

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
    assert np.sum(result.index.mask) == (np.sum(cm.index.mask) - 2)

    # there is now explicit correlation between the observed colors given that:
    #   u-g - (u-r) + g-i - (r-i) = 0
    assert np.isclose(result.cov[0, 0], 7.5e-5)  # var(u-g)
    assert np.isclose(result.cov[0, 1], 2.5e-5)  # cov(u-g, u-r)
    assert np.isclose(result.cov[0, 6], -2.5e-5)  # cov(u-g, g-i)
    assert np.isclose(result.cov[0, 9], 2.5e-5)  # cov(u-g, r-i)


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

    cm = ColorMatrix.from_colors(colors)
    assert cm["u", "i"] is None
    assert cm["u", "g"] is None

    result = solve(cm)
    assert np.isclose(result["u", "i"].index.value, 1.75)
    assert np.isclose(result["u", "g"].index.value, 1.21)

    assert np.isclose(result["u", "i"].unc.value, np.sqrt(2) * 0.01)
    assert np.isclose(result["u", "g"].unc.value, np.sqrt(3) * 0.01)

    # Again, but add a u-i measurement with high uncertainty.  The final u-g
    # should have similar uncertainty to the previous run.
    colors = [
        Color("u", "z", 1.76, 0.01),
        Color("g", "i", 0.54, 0.01),
        Color("i", "z", 0.01, 0.01),
        Color("u", "i", 1.75, 0.10),
    ]

    cm = ColorMatrix.from_colors(colors)
    assert cm["u", "g"] is None

    result = solve(cm)
    assert np.isclose(result["u", "i"].index.value, 1.75)
    assert np.isclose(result["u", "g"].index.value, 1.21)

    assert np.isclose(
        result["u", "i"].unc.value, (1 / 0.1**2 + 1 / (2 * 0.01**2)) ** -0.5
    )

    var1 = 3 * 0.01**2  # u-g = u-z - (i-z) - (g-i)
    var2 = 0.1**2 + 0.01**2  # u-g = u-i - (g-i)
    cov12 = 0.01**2  # g-i is in both
    expected = np.sqrt((var1 * var2 - cov12**2) / (var1 + var2 - 2 * cov12))
    assert np.isclose(result["u", "g"].unc.value, expected)


def test_closed_set():
    """Solve an overdetermined set of colors.

    Three independent measurements, zero degrees of freedom.

    """

    # solar colors from Willmer 2018
    colors = [
        Color("u", "g", 1.21, 0.01),
        Color("u", "r", 1.63, 0.01),
        Color("g", "r", 0.42, 0.01),
    ]

    cm = ColorMatrix.from_colors(colors)
    result = solve(cm)

    # check values
    assert np.isclose(result.index[0], 1.21)  # u-g
    assert np.isclose(result.index[1], 1.63)  # u-r
    assert np.isclose(result.index[5], 0.42)  # g-r

    # check variances
    var = (1 / 0.01**2 + 1 / (2 * 0.01**2)) ** -1
    assert np.isclose(result.cov[0, 0], var)  # var(u-g)
    assert np.isclose(result.cov[1, 1], var)  # var(u-r)
    assert np.isclose(result.cov[5, 5], var)  # var(g-r)

    # check covariances
    cov = 1 / (1 / var + 1 / var)
    assert np.isclose(result.cov[0, 1], cov)  # cov(u-g, u-r)
    assert np.isclose(result.cov[0, 5], -cov)  # cov(u-g, g-r)
    assert np.isclose(result.cov[1, 5], cov)  # cov(u-r, g-r)


def test_multiple():
    """Combine multiple color matrices."""

    cm1 = ColorMatrix.from_colors(
        [
            Color("u", "g", 1.21, 0.01),
            Color("u", "r", 1.63, 0.01),
            Color("g", "r", 0.42, 0.01),
        ]
    )

    cm2 = ColorMatrix.from_colors(
        [
            Color("u", "g", 1.20, 0.01),
            Color("u", "r", 1.61, 0.01),
            Color("g", "r", 0.41, 0.01),
        ]
    )

    result = solve(cm1, cm2)

    # check values, should be the average of the above
    assert np.isclose(result.index[0], 1.205)  # u-g
    assert np.isclose(result.index[1], 1.620)  # u-r
    assert np.isclose(result.index[5], 0.415)  # g-r

    # check variances
    var1 = (1 / 0.01**2 + 1 / (2 * 0.01**2)) ** -1
    var = 1 / (1 / var1 + 1 / var1)
    assert np.isclose(result.cov[0, 0], var)  # var(u-g)
    assert np.isclose(result.cov[1, 1], var)  # var(u-r)
    assert np.isclose(result.cov[5, 5], var)  # var(g-r)

    # check covariances
    cov = 1 / (1 / var + 1 / var)
    assert np.isclose(result.cov[0, 1], cov)  # cov(u-g, u-r)
    assert np.isclose(result.cov[0, 5], -cov)  # cov(u-g, g-r)
    assert np.isclose(result.cov[1, 5], cov)  # cov(u-r, g-r)

    # check that single color matrices work
    cm1 = ColorMatrix.from_colors([Color("u", "g", 1.21, 0.01)])
    cm2 = ColorMatrix.from_colors([Color("g", "r", 0.42, 0.01)])
    result = solve(cm1, cm2)

    # check values
    assert np.isclose(result.index[0], 1.21)  # u-g
    assert np.isclose(result.index[5], 0.42)  # g-r

    # check covariance matrix
    var = 0.01**2
    expected = np.ma.zeros((15, 15))
    expected.mask = True
    expected[0, 0] = var
    expected[0, 1] = var
    expected[0, 5] = 0
    expected[1, 0] = var
    expected[1, 1] = 2 * var
    expected[1, 5] = var
    expected[0, 5] = 0
    expected[1, 5] = var
    expected[5, 5] = var
    assert np.ma.allclose(result.cov, expected)


def test_disjoint():
    # single colors that do not overlap
    cm1 = ColorMatrix.from_colors([Color("u", "g", 1.21, 0.01)])
    cm2 = ColorMatrix.from_colors([Color("r", "i", 0.12, 0.01)])

    result = solve(cm1, cm2)

    expected = ColorMatrix()
    expected.index[[0, 9]] = [1.21, 0.12]
    expected.cov[0, 0] = 0.01**2
    expected.cov[9, 9] = 0.01**2
    assert np.ma.allclose(result.index, expected.index)
    assert np.ma.allclose(result.cov, expected.cov)
