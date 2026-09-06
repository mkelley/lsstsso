import numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.table import Table
from astropy.time import Time


def sky_and_time(
    coords1: SkyCoord, t1: Time, tol1: u.Quantity, coords2: SkyCoord, t2: Time
):
    """Find nearest neighbors on the sky and within a time tolerance."""

    matches = []
    for n, c in enumerate(coords1):
        # first, trim by time tolerance
        dt = (t1[n] - t2).jd * 86400
        i = np.abs(dt) < tol1[n].to_value("s")

        if not any(i):
            continue

        sep = c.separation(coords2[i])

        if sum(i) == 1:
            matches.append(
                {
                    "n": np.argmax(i),
                    "coords1": coords1[n],
                    "t1": t1[n],
                    "coords2": coords2[0],
                    "t2": t2[0],
                    "sep": sep[0],
                }
            )
            continue

        # multiple results, pick the nearest neighbor
        d = np.min(sep)
        nearest = np.flatnonzero(i)[np.argmin(sep)]
        matches.append(
            {
                "n": n,
                "coords1": coords1[n],
                "t1": t1[n],
                "coords2": coords2[nearest],
                "t2": t2[nearest],
                "sep": d,
            }
        )

    return Table(matches)
