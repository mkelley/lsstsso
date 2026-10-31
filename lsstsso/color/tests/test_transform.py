import astropy.units as u
import numpy as np

from ..color import Color
from ..color_matrix import ColorMatrix
from ..transform import transform
from ...band import Band


def test_transform():
    colors = [
        Color(Band.u, Band.g, 1, 0.1),
        Color(Band.g, Band.r, 2, 0.2),
    ]

    cm = ColorMatrix(colors)

    m, unc = transform(0 * u.mag, 0.1, Band.u, Band.g, cm)
    assert u.isclose(m, -1 * u.mag)
    assert u.isclose(unc, np.hypot(0.1, 0.1) * u.mag)

    m, unc = transform(2 * u.mag, 0.01, Band.r, Band.g, cm)
    assert u.isclose(m, 4 * u.mag)
    assert u.isclose(unc, np.hypot(0.01, 0.2) * u.mag)
