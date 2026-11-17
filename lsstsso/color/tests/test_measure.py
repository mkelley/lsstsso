import astropy.units as u
import numpy as np

from ..color import Color
from ..measure import measure


def test_color():
    m = [1, 2, 4] * u.mag
    unc = [0.01, 0.02, 0.04] * u.mag
    bands = ["u", "g", "r"]

    colors = measure(m, unc, bands)
    assert colors[0] == Color("u", "g", -1, np.hypot(0.01, 0.02))
    assert colors[1] == Color("g", "r", -2, np.hypot(0.02, 0.04))

    colors = measure(m, unc, bands, anchor="r")
    assert colors[0] == Color("u", "r", -3, np.hypot(0.01, 0.04))
    assert colors[1] == Color("g", "r", -2, np.hypot(0.02, 0.04))
