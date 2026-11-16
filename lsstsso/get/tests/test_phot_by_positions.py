import astropy.units as u
import pytest
from astropy.table import Table

from ... import get


@pytest.mark.remote_data
def test_phot_by_positions():

    ra = [287.2315412417827] * u.deg
    dec = [-23.851685147435273] * u.deg
    sources = Table([ra, dec], names=["ra", "dec"])
    result = get.phot_by_positions(sources)

    assert u.allclose(result["ra"], ra)
    assert u.allclose(result["dec"], dec)
