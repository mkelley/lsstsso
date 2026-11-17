import astropy.units as u
import numpy as np
import pytest

from ..scale import activity, color, geometry


def test_activity():
    rh = [1, 2, 3] * u.au
    delta = [2, 3, 4] * u.au

    scale = activity(rh, delta, 0, 0)
    assert np.allclose(scale, 0 * u.mag)

    scale = activity(rh, delta, -2, 0)
    assert np.allclose(scale, 2.5 * np.log10(rh.value**2) * u.mag)

    scale = activity(rh, delta, 0, -1)
    assert np.allclose(scale, 2.5 * np.log10(delta.value**1) * u.mag)


def test_color():
    m = [1, 2, 4] * u.mag
    unc = [0.01, 0.02, 0.04] * u.mag
    bands = ["u", "g", "r"]

    scale, _ = color(m, unc, bands, "r")
    assert u.allclose(scale, [3, 2, 0] * u.mag)


@pytest.mark.xfail
def test_color_uncertainties():
    m = [1, 2, 4] * u.mag
    unc = [0.01, 0.02, 0.04] * u.mag
    bands = ["u", "g", "r"]

    _, scale_unc = color(m, unc, bands, "r")

    # these uncertainties are not right, u-g and g-r should be correlated
    assert u.allclose(
        scale_unc,
        [
            np.hypot(0.02, 0.04),
            np.hypot(0.01, 0.02),
            0,
        ]
        * u.mag,
    )


def test_geometry():
    rh = [1, 2, 4] * u.au
    delta = [1, 3, 4] * u.au

    scale = geometry(rh, delta)
    expected = 2.5 * np.log10([1, 4 * 9, 16**2]) * u.mag
    assert np.allclose(scale, expected)

    # now account for phase effect, change delta scaling
    phase = [0, 10, 20] * u.deg

    def Phi(phase):
        return 10 ** (-0.4 * 0.04 * phase.to_value("deg"))

    scale = geometry(rh, delta, phase, delta_slope=-1, Phi=Phi)
    expected = (
        2.5 * np.log10([1, 4, 16]) + 2.5 * np.log10([1, 3, 4]) + np.array([0, 0.4, 0.8])
    ) * u.mag
    assert np.allclose(scale, expected)

    # change activity and delta scaling
    scale = geometry(rh, delta, phase, activity_slope=-2, delta_slope=-2, Phi=Phi)
    expected = (
        2.5 * np.log10([1, 2**4, 4**4])
        + 2.5 * np.log10([1, 9, 16])
        + np.array([0, 0.4, 0.8])
    ) * u.mag
    assert np.allclose(scale, expected)
