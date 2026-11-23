import astropy.units as u
import numpy as np

from ...band import Band
from ..color import Color
from ..color_matrix import ColorMatrix


def test_transform():
    colors = [
        Color(Band.u, Band.g, 1, 0.1),
        Color(Band.g, Band.r, 2, 0.2),
    ]

    cm = ColorMatrix.from_colors(colors)

    m, unc = cm.transform(0 * u.mag, 0.1 * u.mag, Band.u, Band.g)
    assert u.isclose(m, -1 * u.mag)
    assert u.isclose(unc, np.hypot(0.1, 0.1) * u.mag)

    m, unc = cm.transform(2 * u.mag, 0.01 * u.mag, Band.r, Band.g)
    assert u.isclose(m, 4 * u.mag)
    assert u.isclose(unc, np.hypot(0.01, 0.2) * u.mag)

    m, unc = cm.transform(2 * u.mag, 0.01 * u.mag, Band.r, Band.r)
    assert u.isclose(m, 2 * u.mag)
    assert u.isclose(unc, 0.01 * u.mag)

    m, unc = cm.transform(2 * u.mag, 0.01 * u.mag, Band.i, Band.r)
    assert m is np.ma.masked
    assert unc is np.ma.masked


def test_transform_multiple():
    m1 = [1, 2, 4, 8] * u.mag
    unc1 = [0.01, 0.02, 0.04, 0.08] * u.mag
    bands = ["u", "g", "r", "i"]

    cm = ColorMatrix.from_colors(
        [
            Color("u", "r", -3, 0.01),
            Color("g", "r", -2, 0.01),
        ]
    )

    m2, unc2 = cm.transform(m1, unc1, bands, "r")

    assert u.allclose(m2[:3].data, [4, 4, 4] * u.mag)
    assert m2[3].mask

    assert u.allclose(
        unc2[:3].data,
        [np.hypot(0.01, 0.01), np.hypot(0.02, 0.01), 0.04] * u.mag,
    )
    assert unc2[3].mask

    # we can also pass a single band for all measurements
    m2, unc2 = cm.transform(m1, unc1, "g", "r")
    assert len(m2) == len(unc2) == 4
