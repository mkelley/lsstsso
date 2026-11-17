import astropy.units as u
import pytest
from astropy.table import Table
from astropy.time import Time

from ... import get


@pytest.mark.remote_data
def test_phot_by_positions():
    ra = [287.2315412417827] * u.deg
    dec = [-23.851685147435273] * u.deg
    sources = Table([ra, dec], names=["ra", "dec"])

    result = get.phot_by_positions(sources)
    assert u.allclose(result["ra"], ra)
    assert u.allclose(result["dec"], dec)

    ra = [360 - 4.575134, 360 - 16.581423] * u.deg
    dec = [-0.101405, -3.830839] * u.deg
    sources = Table([ra, dec], names=["ra", "dec"])
    result = get.phot_by_positions(
        sources, table="Source", constraints="visit.expMidptMJD < 60900"
    )
    assert len(result) == 2  # two sources near the first observation
    assert all(result.expMidptMJD < Time(60900, format="mjd", scale="tai"))


def test_phot_by_positions_failures():
    ra = [287.2315412417827] * u.deg
    dec = [-23.851685147435273] * u.deg
    sources = Table([ra, dec], names=["ra", "dec"])

    with pytest.raises(ValueError):
        get.phot_by_positions(sources, table="does not exist")
