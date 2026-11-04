import astropy.units as u

from ...band import Band
from ..color import Color


def test_init():
    c = Color(Band.u, Band.g, 1.0, 0.1)
    assert c.left == Band.u
    assert c.right == Band.g
    assert u.isclose(c.index, 1.0 * u.mag)
    assert u.isclose(c.unc, 0.1 * u.mag)

    # strings are OK
    c = Color("r", "g", -1.0, 0.1)
    assert c.left == Band.r
    assert c.right == Band.g
    assert u.isclose(c.index, -1.0 * u.mag)
    assert u.isclose(c.unc, 0.1 * u.mag)

    c = Color("r", "g", [1, 2, 3], [0.1, 0.2, 0.3])
    assert c.left == Band.r
    assert c.right == Band.g
    assert u.allclose(c.index, [1, 2, 3] * u.mag)
    assert u.allclose(c.unc, [0.1, 0.2, 0.3] * u.mag)


def test_str():
    c = Color("u", "g", 1.0, 0.1)
    assert str(c) == "u-g = 1.000 ± 0.100 mag"

    c = Color("u", "g", [1, 2], [0.1, 0.1])
    assert str(c) == "u-g = 1.500 ± 0.071 mag (mean of 2 points)"


def test_mean():
    c = Color("g", "r", [0.4, 0.45] * u.mag, [0.1, 0.05] * u.mag)
    m = c.mean()
    assert m.left == Band.g
    assert m.right == Band.r
    assert u.isclose(m.index, 0.44 * u.mag)
    assert u.isclose(m.unc, 0.044721359549995794 * u.mag)
