import astropy.units as u
import numpy as np

from ..color import Color
from ...band import Band


def test_init():
    c = Color("u", "g", 1.0, 0.1)
    assert c.blue == Band.u
    assert c.red == Band.g
    assert u.isclose(c.index, 1.0 * u.mag)
    assert u.isclose(c.unc, 0.1 * u.mag)

    c = Color("r", "g", -1.0, 0.1)
    assert c.blue == Band.g
    assert c.red == Band.r
    assert u.isclose(c.index, 1.0 * u.mag)
    assert u.isclose(c.unc, 0.1 * u.mag)

    c = Color("r", "g", [1, 2, 3], [0.1, 0.2, 0.3])
    assert c.blue == Band.g
    assert c.red == Band.r
    assert u.allclose(c.index, [-1, -2, -3] * u.mag)
    assert u.allclose(c.unc, [0.1, 0.2, 0.3] * u.mag)


def test_str():
    c = Color("u", "g", 1.0, 0.1)
    assert str(c) == "u-g = 1.000 ± 0.100 mag"

    c = Color("u", "g", [1, 2], [0.1, 0.1])
    assert str(c) == "u-g = 1.500 ± 0.071 mag (mean of 2 points)"


def test_mean():
    c = Color("g", "r", [0.4, 0.45] * u.mag, [0.1, 0.05] * u.mag)
    m = c.mean()
    assert m.blue == Band.g
    assert m.red == Band.r
    assert u.isclose(m.index, 0.44 * u.mag)
    assert u.isclose(m.unc, 0.044721359549995794 * u.mag)
