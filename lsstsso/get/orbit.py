from logging import getLogger
from ..rsp import RSP


def orbit(rsp: RSP, constraints: str, columns: list[str] | None = None, cached=True):
    """Query the mpc_orbit table.


    Parameters
    ----------
    constraints : str
        The query constraints.

    columns : list of str, optional
        The columns to return.

    cached : bool, optional
        ``True`` to cache or return a cached query.


    Returns
    -------
    result : Result

    """

    logger = getLogger("lsstsso")
    logger.info("Querying mpc_orbit")

    if columns is None:
        columns = [
            "designation",
            "epoch_mjd",
            "a",
            "q",
            "e",
            "i",
            "node",
            "argperi",
            "peri_time",
            "a1",
            "a2",
            "a3",
            "dt",
            "period",
            "nobs_total",
        ]

    query = f"""
SELECT {",".join(columns)} FROM dp2.mpc_orbits
WHERE '{constraints}'
"""
    logger.debug(query)

    return rsp.query_tap(query, cache=cached)
