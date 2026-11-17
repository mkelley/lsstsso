import astropy.units as u
import numpy as np
import pytest
from astropy.coordinates import SkyCoord
from astropy.table import Table

from ..band import Band
from ..result import Result


def test_init():
    tab = Table(
        (
            [1, 2, 3] * u.deg,
            [4, 5, 6] * u.deg,
            [60000, 60001, 60002],
            [61000, 61001, 61002],
            [62000, 62001, 62002],
            [60000, 60000, 60000],
            ["g", "r", "z"],
            [1, 2, 3] * u.au,
            [10, 20, 30],
            u.Quantity([1, 2, 3], None),
            SkyCoord([1, 2, 3] * u.deg, [4, 5, 6] * u.deg),
        ),
        names=[
            "ra",
            "dec",
            "midpointMjdTai",
            "expMidptMJD",
            "peri_time",
            "epoch_mjd",
            "band",
            "q",
            "node",
            "e",
            "coords",
        ],
    )

    result = Result(tab)

    assert u.allclose(result.ra, [1, 2, 3] * u.deg)
    assert u.allclose(result.dec, [4, 5, 6] * u.deg)


def test_from_arrays():
    result = Result.from_arrays(ra=[1, 2, 3] * u.deg, dec=[3, 4, 5] * u.deg)
    assert len(result) == 3
    assert u.allclose(result.ra, [1, 2, 3] * u.deg)
    assert u.allclose(result.dec, [3, 4, 5] * u.deg)


def test_from_rows():
    result = Result.from_rows(
        [
            {
                "ra": 1 * u.deg,
                "dec": 2 * u.deg,
            },
            {
                "ra": 3 * u.deg,
                "dec": 4 * u.deg,
            },
            {
                "ra": 5 * u.deg,
                "dec": 6 * u.deg,
            },
        ],
    )
    assert len(result) == 3
    assert u.allclose(result.ra, [1, 3, 5] * u.deg)
    assert u.allclose(result.dec, [2, 4, 6] * u.deg)


def test_length():
    result = Result.from_arrays(a=np.arange(5))
    assert len(result) == 5

    with pytest.raises(ValueError):
        result.columns.append("b")
        result.b = np.arange(4)
        len(result)

    assert len(Result.from_arrays(a=[], b=[])) == 0

    assert len(Result(Table())) == 0


def test_getitem():
    tab = Table(
        (
            [1, 2, 3] * u.deg,
            [4, 5, 6],
        ),
        names=[
            "ra",
            "e",
        ],
    )

    result = Result(tab)

    assert len(result) == 3
    assert np.size(result[0].ra) == 1
    assert np.size(result[0].e) == 1

    assert len(result[:2]) == 2

    assert u.allclose(result[[0, 2]].ra, [1, 3] * u.deg)
    assert len(result[result.e > 4]) == 2


def test_as_table():
    result = Result.from_arrays(
        ra=[1, 2, 3] * u.deg, band=np.array([Band.g, Band.r, Band.y])
    )
    tab = result.as_table()
    assert u.allclose(tab["ra"], [1, 2, 3] * u.deg)
    assert all(tab["band"] == ["g", "r", "y"])


def test_rows():
    result = Result.from_arrays(
        ra=[1, 2, 3] * u.deg, band=np.array([Band.g, Band.r, Band.y])
    )
    for row, ra, band in zip(result.rows(), [1, 2, 3] * u.deg, "gry"):
        assert u.isclose(row.ra, ra)
        assert row.band == band
