import astropy.units as u
import numpy as np
import pytest

from ...band import Band
from ..color import Color
from ..color_matrix import ColorMatrix


def test_transform():
    colors = [
        Color(Band.u, Band.g, 1, 0.1),
        Color(Band.g, Band.r, 2, 0.2),
    ]

    cm = ColorMatrix(colors)

    m, unc = cm.transform(0 * u.mag, 0.1 * u.mag, Band.u, Band.g)
    assert u.isclose(m, -1 * u.mag)
    assert u.isclose(unc, np.hypot(0.1, 0.1) * u.mag)

    m, unc = cm.transform(2 * u.mag, 0.01 * u.mag, Band.r, Band.g)
    assert u.isclose(m, 4 * u.mag)
    assert u.isclose(unc, np.hypot(0.01, 0.2) * u.mag)

    m, unc = cm.transform(2 * u.mag, 0.01 * u.mag, Band.r, Band.r)
    assert u.isclose(m, 2 * u.mag)
    assert u.isclose(unc, 0.01 * u.mag)


def test_transform_fail():
    colors = [
        Color(Band.u, Band.g, 1, 0.1),
        Color(Band.g, Band.r, 2, 0.2),
    ]

    cm = ColorMatrix(colors)

    with pytest.raises(ValueError):
        cm.transform(0 * u.mag, 0.1, Band.u, Band.r)
