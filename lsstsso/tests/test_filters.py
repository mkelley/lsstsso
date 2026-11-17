import astropy.units as u
import pytest
from astropy.coordinates import SkyCoord
from astropy.time import Time

from ..filters import sky, sky_and_time
from ..result import Result


def test_sky():
    coords = SkyCoord([12.34567, 12.34567] * u.deg, [1.234567, 1] * u.deg)
    result = Result.from_arrays(
        ra=[12.34567, 12.34567, 12.34567] * u.deg,
        dec=[
            1.234567 * u.deg + 1 * u.arcsec,
            1.234567 * u.deg + 2 * u.arcsec,
            1.234567 * u.deg - 1.5 * u.arcsec,
        ],
    )

    matches = sky(coords, result)
    assert len(matches) == 2
    assert all(matches.n == [0, 1])
    assert u.allclose(matches.coords.ra, coords.ra)
    assert u.allclose(matches.coords.dec, coords.dec)
    assert all(matches.nearest == [0, 2])
    assert u.allclose(matches.nearest_coords.ra, result.ra[[0, 2]])
    assert u.allclose(matches.nearest_coords.dec, result.dec[[0, 2]])
    assert u.allclose(matches.sep, [1 * u.arcsec, 0.234567 * u.deg - 1.5 * u.arcsec])
    assert u.allclose(matches.pa, [0, 0] * u.deg)


def test_sky_requirements():
    coords = SkyCoord([12.34567, 12.34567] * u.deg, [1.234567, 1] * u.deg)
    result = Result.from_arrays(
        ra=[12.34567, 12.34567, 12.34567] * u.deg,
    )
    with pytest.raises(KeyError):
        sky(coords, result)

    result = Result.from_arrays(
        dec=[
            1.234567 * u.deg + 1 * u.arcsec,
            1.234567 * u.deg + 2 * u.arcsec,
            1.234567 * u.deg - 1.5 * u.arcsec,
        ],
    )
    with pytest.raises(KeyError):
        sky(coords, result)


def test_sky_and_time():
    coords = SkyCoord([12.34567, 12.34567] * u.deg, [1.234567, 1] * u.deg)
    t = Time([60000, 60001], format="mjd", scale="tai")
    for time_key in ["midpointMjdTai", "expMidptMJD"]:
        result = Result.from_arrays(
            **{
                "ra": [12.34567, 12.34567, 12.34567] * u.deg,
                "dec": [
                    1.234567 * u.deg + 1 * u.arcsec,
                    1.234567 * u.deg + 2 * u.arcsec,
                    1.234567 * u.deg - 1.5 * u.arcsec,
                ],
                time_key: [60001, 60000, 59999],
            },
        )

        matches = sky_and_time(coords, t, result)
        assert len(matches) == 2
        assert all(matches["n"] == [0, 1])
        assert u.allclose(matches["coords"].ra, coords.ra)
        assert u.allclose(matches["coords"].dec, coords.dec)
        assert all(matches["nearest"] == [1, 0])
        assert u.allclose(matches.nearest_coords.ra, result.ra[[1, 0]])
        assert u.allclose(matches.nearest_coords.dec, result.dec[[1, 0]])
        assert u.allclose(
            matches["sep"], [2 * u.arcsec, 0.234567 * u.deg + 1 * u.arcsec]
        )
        assert u.allclose(matches.pa, [0, 0] * u.deg)

    # test nothing close in time
    t = Time([60010, 60011], format="mjd", scale="tai")
    matches = sky_and_time(coords, t, result)
    assert len(matches) == 0


def test_sky_and_time_requirements():
    a = SkyCoord([12.34567, 12.34567] * u.deg, [1.234567, 1] * u.deg)
    ra = [12.34567, 12.34567, 12.34567] * u.deg
    dec = [
        1.234567 * u.deg + 1 * u.arcsec,
        1.234567 * u.deg + 2 * u.arcsec,
        1.234567 * u.deg - 1.5 * u.arcsec,
    ]
    t = Time([60001, 60000, 59999], format="mjd", scale="tai")

    result = Result.from_arrays(ra=ra, dec=dec)
    with pytest.raises(KeyError):
        sky_and_time(a, t, result)

    result = Result.from_arrays(ra=ra, midpointMjdTai=t)
    with pytest.raises(KeyError):
        sky_and_time(a, t, result)

    result = Result.from_arrays(ra=ra, expMidptMJD=t)
    with pytest.raises(KeyError):
        sky_and_time(a, t, result)

    result = Result.from_arrays(dec=dec, expMidptMJD=t)
    with pytest.raises(KeyError):
        sky_and_time(a, t, result)
