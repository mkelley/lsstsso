from logging import getLogger
from .. import rsp
from ..result import ResultClass


def orbit(
    constraints: str, columns: list[str] | None = None, cached=True
) -> ResultClass:
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

    with rsp.provider() as _rsp:
        return _rsp.query_tap(query, cache=cached)
