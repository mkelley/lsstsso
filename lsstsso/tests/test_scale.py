import astropy.units as u
import numpy as np

from ..scale import activity, geometry


def test_activity():
    rh = [1, 2, 3] * u.au
    delta = [2, 3, 4] * u.au

    scale = activity(rh, delta, 0, 0)
    assert np.allclose(scale, 0 * u.mag)

    scale = activity(rh, delta, -2, 0)
    assert np.allclose(scale, 2.5 * np.log10(rh.value**2) * u.mag)

    scale = activity(rh, delta, 0, -1)
    assert np.allclose(scale, 2.5 * np.log10(delta.value**1) * u.mag)


def test_geometry_simple_rh():
    rh = [1, 1, 1] * u.au
    delta = [1, 1, 1] * u.au

    scale = geometry(rh, delta, activity_slope=0, delta_slope=-2)
    assert u.allclose(scale, [0, 0, 0] * u.mag)

    rh = [1, 2, 4] * u.au
    scale = geometry(rh, delta, activity_slope=0, delta_slope=-2)
    assert u.allclose(scale, 5 * np.log10(rh.value) * u.mag)

    rh = [1, 2, 4] * u.au
    scale = geometry(rh, delta, activity_slope=-8, delta_slope=-2)
    assert u.allclose(
        scale, (5 * np.log10(rh.value) - 2.5 * np.log10(rh.value**-8)) * u.mag
    )

    assert u.allclose(scale, -2.5 * np.log10(rh.value**-10) * u.mag)


def test_geometry_simple_delta():
    rh = [1, 1, 1] * u.au
    delta = [1, 2, 4] * u.au
    scale = geometry(rh, delta, activity_slope=0, delta_slope=-2)
    assert u.allclose(scale, 5 * np.log10(delta.value) * u.mag)


def test_geometry_simple_phi():
    rh = [1, 1, 1] * u.au
    delta = [1, 1, 1] * u.au
    phase = [0, 30, 90] * u.deg

    def Phi(phase):
        return 10 ** (-0.4 * 0.04 * phase.to_value("deg"))

    scale = geometry(rh, delta, phase, activity_slope=0, delta_slope=0, Phi=Phi)
    assert u.allclose(scale, [0, 0.04 * 30, 0.04 * 90] * u.mag)


def test_geometry_combo():
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
