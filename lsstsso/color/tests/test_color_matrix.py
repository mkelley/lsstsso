import astropy.units as u
import numpy as np
from numpy.linalg import norm

from ...band import Band
from ..color import Color
from ..color_matrix import ColorMatrix


def test_init():
    colors = [
        Color(Band.u, Band.g, 1.0, 0.2),
        Color(Band.g, Band.i, 1.3, 0.1),
        Color(Band.g, Band.y, 0.25, 0.055),
        Color(Band.r, Band.i, 0.2, 0.05),
        Color(Band.z, Band.y, 0.11, 0.01),
    ]

    cm = ColorMatrix(colors)

    expected = np.ma.masked_array(
        [
            [0, 1.0, 0, 0, 0, 0],
            [-1.0, 0, 0, 1.3, 0, 0.25],
            [0, 0, 0, 0.2, 0, 0],
            [0, -1.3, -0.2, 0, 0, 0],
            [0, 0, 0, 0, 0, 0.11],
            [0, -0.25, 0, 0, -0.11, 0],
        ]
    )
    expected.mask = expected == 0
    assert np.ma.allclose(cm.index, expected)

    expected = np.ma.masked_array(
        [
            [0, 0.2, 0, 0, 0, 0],
            [0.2, 0, 0, 0.1, 0, 0.055],
            [0, 0, 0, 0.05, 0, 0],
            [0, 0.1, 0.05, 0, 0, 0],
            [0, 0, 0, 0, 0, 0.01],
            [0, 0.055, 0, 0, 0.01, 0],
        ]
    )
    expected.mask = expected == 0
    assert np.ma.allclose(cm.unc, expected)


def test_init_averaging():
    colors = [
        Color(Band.u, Band.g, 1.0, 0.2),
        Color(Band.u, Band.g, 0.8, 0.2),
        Color(Band.g, Band.r, 1.2, 0.02),
        Color(Band.r, Band.g, -1.4, 0.02),
        Color(Band.u, Band.i, [0.8, 0.6], [0.1, 0.1]),
    ]

    cm = ColorMatrix(colors)

    color = cm["u", "g"]
    assert u.isclose(color.index, 0.9 * u.mag)
    assert u.isclose(color.unc, np.hypot(0.2, 0.2) / 2 * u.mag)

    color = cm["g", "r"]
    assert u.isclose(color.index, 1.3 * u.mag)
    assert u.isclose(color.unc, np.hypot(0.02, 0.02) / 2 * u.mag)

    color = cm["u", "i"]
    assert u.isclose(color.index, 0.7 * u.mag)
    assert u.isclose(color.unc, np.hypot(0.1, 0.1) / 2 * u.mag)


def test_getitem():
    colors = [Color(Band.u, Band.g, 1.0, 0.2)]

    cm = ColorMatrix(colors)

    c = cm["u", "g"]
    assert c.left == Band.u
    assert c.right == Band.g
    assert u.isclose(c.index, 1.0 * u.mag)
    assert u.isclose(c.unc, 0.2 * u.mag)


def test_fill():
    colors = [
        Color(Band.u, Band.g, 1, 0.1),
        Color(Band.g, Band.r, 2, 0.2),
        Color(Band.r, Band.i, 3, 0.3),
        Color(Band.i, Band.z, 4, 0.4),
        Color(Band.z, Band.y, 5, 0.5),
    ]

    cm = ColorMatrix(colors)

    expected = np.ma.masked_array(
        [
            [0, 1, 3, 6, 10, 15],
            [-1, 0, 2, 5, 9, 14],
            [-3, -2, 0, 3, 7, 12],
            [-6, -5, -3, 0, 4, 9],
            [-10, -9, -7, -4, 0, 5],
            [-15, -14, -12, -9, -5, 0],
        ]
    )
    expected.mask = expected == 0
    assert np.ma.allclose(cm.index, expected)

    unc = np.arange(1, 6) / 10
    expected = np.ma.masked_array(
        [
            [
                0,
                0.1,
                norm(unc[:2]),
                norm(unc[:3]),
                norm(unc[:4]),
                norm(unc),
            ],
            [
                0.1,
                0,
                0.2,
                norm(unc[1:3]),
                norm(unc[1:4]),
                norm(unc[1:]),
            ],
            [
                norm(unc[:2]),
                0.2,
                0.0,
                0.3,
                norm(unc[2:4]),
                norm(unc[2:]),
            ],
            [
                norm(unc[:3]),
                norm(unc[1:3]),
                unc[2],
                0.0,
                unc[3],
                norm(unc[3:]),
            ],
            [
                norm(unc[:4]),
                norm(unc[1:4]),
                norm(unc[2:4]),
                unc[3],
                0,
                norm(unc[4:]),
            ],
            [
                norm(unc),
                norm(unc[1:]),
                norm(unc[2:]),
                norm(unc[3:]),
                unc[4],
                0,
            ],
        ]
    )
    expected[expected == 0] = np.ma.masked
    assert np.ma.allclose(cm.unc, expected)

    # for this case, make sure the u - i color takes precedence and that there
    # are no z or y colors
    colors = [
        Color(Band.u, Band.g, 1, 0.1),
        Color(Band.u, Band.i, 6.05, 0.02),
        Color(Band.g, Band.r, 2, 0.2),
        Color(Band.r, Band.i, 3, 0.3),
    ]

    cm = ColorMatrix(colors)

    expected = np.ma.masked_array(
        [
            [0, 1, 3, 6.05, 0, 0],
            [-1, 0, 2, 5.05, 0, 0],
            [-3, -2, 0, 3, 0, 0],
            [-6.05, -5.05, -3, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ]
    )
    expected.mask = expected == 0
    assert np.ma.allclose(cm.index, expected)

    expected = np.ma.masked_array(
        [
            [
                0,
                0.1,
                norm((0.1, 0.2)),
                0.02,
                0,
                0,
            ],
            [
                0.1,
                0,
                0.2,
                norm((0.02, 0.1)),
                0,
                0,
            ],
            [
                norm((0.1, 0.2)),
                0.2,
                0,
                0.3,
                0,
                0,
            ],
            [
                0.02,
                norm((0.02, 0.1)),
                0.3,
                0,
                0,
                0,
            ],
            [
                0,
                0,
                0,
                0,
                0,
                0,
            ],
            [
                0,
                0,
                0,
                0,
                0,
                0,
            ],
        ]
    )
    expected[expected == 0] = np.ma.masked
    assert np.ma.allclose(cm.unc, expected)


def test_read_write(tmp_path):
    colors = [
        Color(Band.u, Band.g, 1.0, 0.2),
        Color(Band.g, Band.i, 1.3, 0.1),
        Color(Band.g, Band.y, 0.25, 0.055),
        Color(Band.r, Band.i, 0.2, 0.05),
        Color(Band.z, Band.y, 0.11, 0.01),
    ]
    cm0 = ColorMatrix(colors)
    cm0.write(tmp_path / "color_matrix.ecsv")

    cm = ColorMatrix.read(tmp_path / "color_matrix.ecsv")

    assert np.allclose(cm.index.data, cm0.index.data)
    assert np.all(cm.index.mask == cm0.index.mask)

    assert np.allclose(cm.unc.data, cm0.unc.data)
    assert np.all(cm.unc.mask == cm0.unc.mask)
