import astropy.units as u
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.table import Table
from astropy.time import Time

from .result import Result


def sky(
    coords: SkyCoord,
    result: Result,
) -> Result:
    """Find nearest neighbors on the sky.


    Parameters
    ----------
    coords : SkyCoord
        The coordinates of interest.

    result : Result
        An RSP result.  Columns "ra" and "dec" will be used.


    Returns
    -------
    matches : Result
        Attributes / columns:
            * ``n``: input coordinate array index number
            * ``coords``: input coordinate
            * ``nearest``: index of the nearest coordinate
            * ``nearest_coords``: nearest coordinate
            * ``sep``: angular distance to nearest coordinate
            * ``pa``: position angle to nearest coordinate

    """

    if len(set(result.columns) & {"ra", "dec"}) != 2:
        raise KeyError("ra and/or dec not in result")

    coords_r = SkyCoord(result["ra"], result["dec"])

    matches = []
    for n, c in enumerate(coords):
        sep = c.separation(coords_r)
        d = np.min(sep)
        nearest = np.argmin(sep)
        pa = c.position_angle(coords_r[nearest])

        matches.append(
            {
                "n": n,
                "coords": c,
                "nearest": nearest,
                "nearest_coords": coords_r[nearest],
                "sep": d.to("arcsec"),
                "pa": pa,
            }
        )

    return Result(Table(matches))


def sky_and_time(
    coords: SkyCoord,
    t: Time,
    result: Result,
    tol: u.Quantity = 15 * u.s,
) -> Result:
    """Find nearest neighbors on the sky and within a time tolerance.


    Parameters
    ----------
    coords : SkyCoord
        The coordinates of interest.

    t : Time
        The time for each coordinate.

    result : Result
        An RSP result.  Columns "ra", "dec", and "midpointMjdTai"/"expMidptMJD"
        will be used.

    tol : Quantity
        The time tolerance.  Default is 15 s.  May be an array for a different
        tolerance with each ``coords``.


    Returns
    -------
    matches : Result
        Attributes / columns:
            * ``n``: input coordinate array index number
            * ``coords``: input coordinate
            * ``t``: input time,
            * ``nearest``: index of the nearest coordinate
            * ``nearest_coords``: nearest coordinate
            * ``nearest_t``: nearest coordinate's time
            * ``dt``: time difference to nearest coordinate
            * ``sep``: angular distance to nearest coordinate
            * ``pa``: position angle to nearest coordinate

    """

    if (
        "ra" not in result.columns
        or "dec" not in result.columns
        or (
            "midpointMjdTai" not in result.columns
            and "expMidptMJD" not in result.columns
        )
    ):
        raise KeyError("ra, dec, and/or midpointMjdTai/expMidptMJD not in result")

    coords_r = SkyCoord(result["ra"], result["dec"])
    if "midpointMjdTai" in result.columns:
        t_r = result.midpointMjdTai
    else:
        t_r = result.expMidptMJD

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
        nearest_time = t_r[i][nearest]

        matches.append(
            {
                "n": n,
                "coords": c,
                "t": t[n],
                "nearest": nearest_result_index,
                "nearest_coords": coords_r[nearest_result_index],
                "nearest_t": nearest_time,
                "dt": dt[nearest_result_index],
                "sep": nearest_sep.to("arcsec"),
                "pa": nearest_pa.to("deg"),
            }
        )

    return Result.from_rows(matches)
