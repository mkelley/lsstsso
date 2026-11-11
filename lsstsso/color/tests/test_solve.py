import numpy as np

from ..color import Color
from ..color_matrix import ColorMatrix


def test_solve_simple():
    colors = [
        Color("u", "r", 2.0, 0.06),
        Color("g", "r", 0.5, 0.013),
    ]

    cm = ColorMatrix(colors)
    result = ColorMatrix(colors, solve=True)

    assert np.isclose(result["u", "g"].index.value, 1.5)
    assert np.isclose(result["u", "g"].unc.value, np.hypot(0.06, 0.013))

    # no other colors should have been filled
    assert np.sum(result.index.mask) == (np.sum(cm.index.mask) - 2)
