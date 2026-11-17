import astropy.units as u
import numpy as np

from ..color import Color
from ..measure import measure


def test_measure():
    m = [1, 4, 2] * u.mag
    unc = [0.01, 0.04, 0.02] * u.mag
    bands = ["u", "r", "g"]

    colors = measure(m, unc, bands)
    assert colors[0] == Color("u", "g", -1, np.hypot(0.01, 0.02))
    assert colors[1] == Color("g", "r", -2, np.hypot(0.02, 0.04))

    colors = measure(m, unc, bands, anchor="r")
    assert colors[0] == Color("u", "r", -3, np.hypot(0.01, 0.04))
    assert colors[1] == Color("g", "r", -2, np.hypot(0.02, 0.04))
