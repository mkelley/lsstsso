import astropy.units as u
import numpy as np

from ...band import Band
from ..color import Color
from ..color_matrix import ColorMatrix


def test_init():
    colors = np.ma.arange(15)
    colors.mask = False
    cov = np.ma.arange(15 * 15).reshape((15, 15))
    cov.mask = False

    colors.mask[10] = True
    cov.mask[:, 10] = True
    cov.mask[10, :] = True

    cm = ColorMatrix(colors, cov)
    assert np.ma.allclose(cm.index, colors)
    assert np.ma.allclose(cm.cov, cov)


def test_from_colors():
    colors = [
        Color(Band.u, Band.g, 1.0, 0.2),
        Color(Band.g, Band.i, 1.3, 0.1),
        Color(Band.g, Band.y, 0.25, 0.055),
        Color(Band.r, Band.i, 0.2, 0.05),
        Color(Band.z, Band.y, 0.11, 0.01),
    ]

    cm = ColorMatrix.from_colors(colors)

    expected = np.array(
        [
            1.0,
            0,
            0,
            0,
            0,
            0,
            1.3,
            0,
            0.25,
            0.2,
            0,
            0,
            0,
            0,
            0.11,
        ]
    )
    expected = np.ma.masked_array(expected, mask=expected == 0)

    assert np.ma.allclose(cm.index.filled(0), expected.filled(0))
    assert np.all(cm.index.mask == expected.mask)

    expected = np.diag(
        [
            0.2**2,
            0,
            0,
            0,
            0,
            0,
            0.1**2,
            0,
            0.055**2,
            0.05**2,
            0,
            0,
            0,
            0,
            0.01**2,
        ]
    )
    expected = np.ma.masked_array(expected, mask=expected == 0)
    assert np.ma.allclose(cm.cov.filled(0), expected.filled(0))
    assert np.all(cm.cov.mask == expected.mask)


def test_getitem():
    colors = [Color(Band.u, Band.g, 1.0, 0.2)]

    cm = ColorMatrix.from_colors(colors)

    c = cm["u", "g"]
    assert c.left == Band.u
    assert c.right == Band.g
    assert u.isclose(c.index, 1.0 * u.mag)
    assert u.isclose(c.unc, 0.2 * u.mag)

    assert cm["u", "r"] is None

    assert cm["u", "u"] == Color("u", "u", 0, 0)


def test_iter():
    colors = [
        Color(Band.u, Band.g, 1.0, 0.2),
        Color(Band.g, Band.r, 1.2, 0.02),
        Color(Band.u, Band.i, 1.4, 0.1),
    ]
    cm = ColorMatrix.from_colors(colors)
    for color in cm:
        assert color in colors


def test_read_write(tmp_path):
    colors = np.ma.arange(15)
    colors.mask = False
    cov = np.ma.arange(15 * 15).reshape((15, 15))
    cov.mask = False

    colors.mask[10] = True
    cov.mask[:, 10] = True
    cov.mask[10, :] = True

    cm0 = ColorMatrix(colors, cov)
    cm0.write(tmp_path / "color_matrix.ecsv")

    cm = ColorMatrix.read(tmp_path / "color_matrix.ecsv")

    assert np.allclose(cm.index.filled(0), cm0.index.filled(0))
    assert np.all(cm.index.mask == cm0.index.mask)

    assert np.allclose(cm.cov.filled(0), cm0.cov.filled(0))
    assert np.all(cm.cov.mask == cm0.cov.mask)
