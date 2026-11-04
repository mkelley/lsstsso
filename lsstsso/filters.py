import astropy.units as u
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.table import Table
from astropy.time import Time

from .result import Result


def sky(
    coords: SkyCoord,
    result: Result,
):
    """Find nearest neighbors on the sky.


    Parameters
    ----------
    coords : SkyCoord
        The nominal coordinates of interest.

    result : Result
        An RSP result.  Columns "ra", "dec", and "midpointMjdTai" will be used.


    Returns
    -------
    matches : Table
        A row for each matched coordinate in ``coords`` containing the array
        index from ``coords``, a copy of the coordinate, the index of the
        nearest result, the identified nearest result coordinate, and the
        angular separation.

    """

    if not (set(result.columns()) & {"ra", "dec"}):
        raise KeyError("ra and/or dec not in result")

    coords_r = SkyCoord(result["ra"], result["dec"])

    matches = []
    for n, c in enumerate(coords):
        sep = c.separation(coords_r)
        d = np.min(sep)
        nearest = np.argmin(sep)

        matches.append(
            {
                "n": n,
                "coords": c,
                "nearest": nearest,
                "nearest coords": coords_r[nearest],
                "sep": d.to("arcsec"),
            }
        )

    return Table(matches)


def sky_and_time(
    coords: SkyCoord,
    t: Time,
    tol: u.Quantity,
    result: Result,
):
    """Find nearest neighbors on the sky and within a time tolerance.


    Parameters
    ----------
    coords : SkyCoord
        The nominal coordinates of interest.

    t : Time
        The time for each coordinate.

    tol : Quantity
        The time tolerance.  Usually equal to 1 s to account for shutter timing.
        May be an array for a different tolerance with each ``coords``.

    result : Result
        An RSP result.  Columns "ra", "dec", and "midpointMjdTai" will be used.


    Returns
    -------
    matches : Table
        A row for each matched coordinate in ``coords`` containing the array
        index from ``coords``, a copy of the coordinate and time, the index of
        the nearest result, the identified nearest result coordinate, the
        difference in time, and the angular separation.

    """

    if not (set(result.columns()) & {"ra", "dec", "midpointMjdTai"}):
        raise KeyError("ra, dec, and/or midpointMjdTai not in result")

    coords_r = SkyCoord(result["ra"], result["dec"])
    t_r = result.midpointMjdTai

    # broadcast tol as needed
    if tol.ndim != coords.ndim:
        tol = np.broadcast_to(tol, coords.shape) * tol.unit

    matches = []
    for n, c in enumerate(coords):
        # first, trim by time tolerance
        dt = (t[n] - t_r).jd * 86400 * u.s
        i = np.abs(dt) < tol[n]

        if not any(i):
            continue

        sep = c.separation(coords_r[i])
        nearest = np.argmin(sep)
        nearest_sep = sep[nearest]
        nearest_pa = c.position_angle(coords_r[i][nearest])
        nearest_result_index = np.flatnonzero(i)[nearest]

        matches.append(
            {
                "n": n,
                "coords": c,
                "t": t[n],
                "nearest": nearest_result_index,
                "nearest coords": coords_r[nearest_result_index],
                "dt": dt[nearest_result_index],
                "sep": nearest_sep.to("arcsec"),
                "pa": nearest_pa.to("deg"),
            }
        )

    return Table(matches)
