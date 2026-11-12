from logging import getLogger

from .. import rsp
from ..result import Result


def ssobject(
    constraints: str,
    columns: list[str] | None = None,
    top: int | None = None,
    cached=True,
    **kwargs,
) -> Result:
    """Query the SSObject and numbered_identifications tables.


    Parameters
    ----------
    constraints : str
        The query constraints.

    columns : list of str
        The columns to return.  SSObject columns may be prefixed with "s.",
        numbered_identifications may be prefixed with "n.", e.g.,
        "s.ssObjectId".

    top : int, optional
        Limit the results to at most ``top`` rows.

    cached : bool, optional
        ``True`` to cache or return a cached query.

    **kwargs
        Other keyword arguments are passed to `RSP.query_tap`.

    Returns
    -------
    result : Result

    """

    logger = getLogger("lsstsso")
    logger.info("Querying SSObject LEFT JOIN numbered_identifications")

    if columns is None:
        columns = [
            "s.ssObjectId",
            "s.designation",
            "s.nObs",
            "s.arc",
            "s.firstObservationMjdTai",
            "s.tisserand_J",
            "n.permid",
        ]

    _top = "" if top is None else f"TOP {top}"

    query = f"""
SELECT {_top} {",".join(columns)} FROM dp2.SSObject AS s
LEFT JOIN dp2.numbered_identifications AS n
ON n.unpacked_primary_provisional_designation = s.designation
WHERE {constraints}
"""
    logger.debug(query)

    with rsp.provider() as _rsp:
        return _rsp.query_tap(query, cache=cached, **kwargs)
