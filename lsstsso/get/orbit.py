from logging import getLogger

from .. import rsp
from ..result import Result


def orbit(
    constraints: str,
    columns: list[str] | None = None,
    top: int | None = None,
    cached=True,
) -> Result:
    """Query the mpc_orbit table.


    Parameters
    ----------
    constraints : str
        The query constraints.

    columns : list of str, optional
        The columns to return.

    top : int, optional
        Limit the results to at most ``top`` rows.

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

    _top = "" if top is None else f"TOP {top}"

    query = f"""
SELECT {_top} {",".join(columns)} FROM dp2.mpc_orbits
WHERE {constraints}
"""
    logger.debug(query)

    with rsp.provider() as _rsp:
        return _rsp.query_tap(query, cache=cached)
