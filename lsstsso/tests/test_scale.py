import astropy.units as u
import numpy as np
import pytest
from astropy.coordinates import SkyCoord
from astropy.table import Table

from ..band import Band
from ..color import Color
from ..scale import activity, color, geometry, weighted_mean


def test_activity():
    rh = [1, 2, 3] * u.au
    delta = [2, 3, 4] * u.au

    scale = activity(rh, delta, 0, 0)
    assert np.allclose(scale, 0)

    scale = activity(rh, delta, -2, 0)
    assert np.allclose(scale, -2.5 * np.log10(rh.value**2))

    scale = activity(rh, delta, 0, -1)
    assert np.allclose(scale, -2.5 * np.log10(delta.value**1))


def test_color():
    m = [1, 2, 4] * u.mag
    unc = [0.01, 0.02, 0.04] * u.mag
    bands = ["u", "g", "r"]

    colors = color(m, unc, bands)
    assert colors[0] == Color("u", "g", -1, np.hypot(0.01, 0.02))
    assert colors[1] == Color("g", "r", -2, np.hypot(0.02, 0.04))

    colors = color(m, unc, bands, anchor="r")
    assert colors[0] == Color("u", "r", -3, np.hypot(0.01, 0.04))
    assert colors[1] == Color("g", "r", -2, np.hypot(0.02, 0.04))


def test_geometry():
    rh = [1, 2, 4] * u.au
    delta = [1, 3, 4] * u.au
    phase = [0, 10, 20] * u.deg

    def Phi(phase):
        return 10 ** (-0.4 * 0.04 * phase.to_value("deg"))

    scale = geometry(rh, delta, phase, activity_slope=0, delta_slope=-1, Phi=Phi)
    expected = (
        -2.5 * np.log10([1, 4, 16])
        - 2.5 * np.log10([1, 3, 4])
        - np.array([0, 0.4, 0.8])
    )
    assert np.allclose(scale, expected)

    scale = geometry(rh, delta, phase, activity_slope=-2, delta_slope=-2, Phi=Phi)
    expected = (
        -2.5 * np.log10([1, 2**4, 4**4])
        - 2.5 * np.log10([1, 9, 16])
        - np.array([0, 0.4, 0.8])
    )
    assert np.allclose(scale, expected)


def test_weighted_mean():
    x = np.array([1, 2])
    xunc = np.array([0.01, 0.01])
    m, munc = weighted_mean(x, xunc)
    assert np.isclose(m, 1.5)
    assert np.isclose(munc, np.sqrt(2) / 2 * 0.01)

    x = np.array([1, 2, np.nan])
    xunc = np.array([0.01, 0.01, 1])
    m, munc = weighted_mean(x, xunc)
    assert np.isclose(m, 1.5)
    assert np.isclose(munc, np.sqrt(2) / 2 * 0.01)

    x = np.array([np.nan, np.nan, np.nan])
    xunc = np.array([0.01, 0.01, 1])
    m, munc = weighted_mean(x, xunc)
    assert np.isnan(m)
    assert np.isnan(munc)

    x = np.array([1, 2])
    xunc = np.array([0.01, 0.02])
    m, munc = weighted_mean(x, xunc)
    assert np.isclose(m, 1.2)
    assert np.isclose(munc, 0.00894427190999916)
