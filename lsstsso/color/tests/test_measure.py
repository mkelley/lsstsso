import astropy.units as u
import numpy as np

from ..color_matrix import ColorMatrix
from ..measure import measure


def test_measure():
    m = [1, 4, 2] * u.mag
    unc = [0.01, 0.04, 0.02] * u.mag
    bands = ["u", "r", "g"]

    cm = measure(m, unc, bands)

    expected = ColorMatrix()
    i = [0, 5]  # u-g, g-r
    expected.index[i] = [-1, -2]
    assert np.ma.allclose(cm.index, expected.index)

    vu, vg, vr = 0.01**2, 0.02**2, 0.04**2  # var
    expected.cov[0, 0] = vu + vg
    expected.cov[5, 5] = vg + vr
    assert np.ma.allclose(cm.cov, expected.cov)

    # should have calculated i-y
    m = [19.862286, 19.74449, 19.96902] * u.mag
    unc = [0.10265709, 0.08439844, 0.02326565] * u.mag
    bands = ["y", "y", "i"]
    cm = measure(m, unc, bands)
    assert len(cm) == 1
    assert cm.index[13] is not np.ma.masked


def test_measure_all():
    m = [1, 4, 2] * u.mag
    unc = [0.01, 0.04, 0.02] * u.mag
    bands = ["u", "r", "g"]

    cm = measure(m, unc, bands, all=True)

    expected = ColorMatrix()
    i = [0, 1, 5]  # u-g, u-r, g-r
    expected.index[i] = [-1, -3, -2]
    assert np.ma.allclose(cm.index, expected.index)

    vu, vg, vr = 0.01**2, 0.02**2, 0.04**2  # var
    expected.cov[0, [0, 1, 5]] = expected.cov[[0, 1, 5], 0] = vu + vg, vu, -vg
    expected.cov[1, [1, 5]] = expected.cov[[1, 5], 1] = vu + vr, vr
    expected.cov[5, 5] = vg + vr
    assert np.ma.allclose(cm.cov, expected.cov)


def test_measure_no_colors():
    m = [1, 4, 2] * u.mag
    unc = [0.01, 0.04, 0.02] * u.mag
    bands = ["u", "u", "u"]

    cm = measure(m, unc, bands, all=True)
    expected = ColorMatrix()
    assert np.ma.allclose(cm.index, expected.index)
    assert np.ma.allclose(cm.cov, expected.cov)
