import astropy.units as u
import numpy as np

from ..measure import measure


def test_measure():
    m = [1, 4, 2] * u.mag
    unc = [0.01, 0.04, 0.02] * u.mag
    bands = ["u", "r", "g"]

    cm = measure(m, unc, bands)
    i = [0, 1, 5]  # u-g, u-r, g-r
    assert np.allclose(cm.index[i], [-1, -3, -2])

    vu, vg, vr = 0.01**2, 0.02**2, 0.04**2  # var

    expected = [
        [vu + vg, vu, -vg],
        [vu, vu + vr, vr],
        [-vg, vr, vg + vr],
    ]
    assert np.allclose(cm.cov[i][:, i], expected)

    # everything else should be masked
    assert cm.index.mask.sum() == 15 - 3
    assert cm.cov.mask.sum() == 15 * 15 - 9
