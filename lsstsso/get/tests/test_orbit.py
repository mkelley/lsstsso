import astropy.units as u
import pytest

from ... import get


@pytest.mark.remote_data
def test_orbit():
    orbit = get.orbit("designation LIKE 'P/%' ORDER BY designation", top=10)
    assert len(orbit) == 10
    assert u.isclose(orbit.q[0], 0.57250766 * u.au)
