import astropy.units as u
import pytest

from ... import get


@pytest.mark.remote_data
def test_lightcurve():
    lc = get.lightcurve(5785498485624156464)
    assert len(lc) == 11
    assert u.isclose(lc[0].ra, 287.2315412417827 * u.deg)
    assert lc.SSObjectId[0] == 5785498485624156464
