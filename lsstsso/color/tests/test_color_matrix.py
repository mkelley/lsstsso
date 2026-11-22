import astropy.units as u
import numpy as np
import pytest

from ...band import Band
from ..color import Color
from ..color_matrix import ColorMatrix


def test_init():
    # test empty arrays
    cm = ColorMatrix()
    assert np.all(cm.index.mask)
    assert np.all(cm.cov.mask)

    index = np.ma.arange(15)
    index.mask = False
    cov = np.ma.arange(15 * 15).reshape((15, 15))
    cov.mask = False

    index.mask[10] = True
    cov.mask[:, 10] = True
    cov.mask[10, :] = True

    cm = ColorMatrix(index, cov)
    assert np.ma.allclose(cm.index, index)
    assert np.ma.allclose(cm.cov, cov)

    # initialize with 1-sigma uncertainties
    cm = ColorMatrix(index, 0.1 * np.ones(15))
    assert np.ma.allclose(cm.unc, 0.1)


def test_init_fail():
    index = np.zeros(14)
    with pytest.raises(ValueError):
        ColorMatrix(index)

    index = np.zeros(15)
    cov = np.zeros((14, 14))
    with pytest.raises(ValueError):
        ColorMatrix(index, cov)

    unc = np.zeros(14)
    with pytest.raises(ValueError):
        ColorMatrix(index, unc)


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


def test_set():
    cm = ColorMatrix()

    cm["u", "g"] = 1 * u.mag, 0.1 * u.mag
    assert u.isclose(cm.index[0], 1)
    assert u.isclose(cm.unc[0], 0.1)

    cm["u", "r"] = 2, 0.2
    assert u.isclose(cm.index[1], 2)
    assert u.isclose(cm.unc[1], 0.2)

    cm.set(Color("g", "r", 1, 0.3))
    assert u.isclose(cm.index[5], 1)
    assert u.isclose(cm.unc[5], 0.3)

    cm.set(Color("i", "r", -1, 0.4))
    assert u.isclose(cm.index[9], 1)
    assert u.isclose(cm.unc[9], 0.4)

    cm["u", "r"] = np.ma.masked, np.ma.masked
    assert cm.index.mask[1]
    assert cm.unc.mask[1]


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
