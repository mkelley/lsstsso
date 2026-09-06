from logging import getLogger
from ..rsp import RSP


def ssobject(
    rsp: RSP,
    constraints: str,
    columns: list[str] | None = None,
    cached=True,
    **kwargs,
):
    """Query the SSObject and numbered_identifications tables.


    Parameters
    ----------
    constraints : str
        The query constraints.

    columns : list of str
        The columns to return.  SSObject columns may be prefixed with "s.",
        numbered_identifications may be prefixed with "n.", e.g.,
        "s.ssObjectId".

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

    query = f"""
SELECT {",".join(columns)} FROM dp2.SSObject AS s
LEFT JOIN dp2.numbered_identifications AS n
ON n.unpacked_primary_provisional_designation = s.designation
WHERE {constraints}
"""
    logger.debug(query)

    return rsp.query_tap(query, cache=cached, **kwargs)
