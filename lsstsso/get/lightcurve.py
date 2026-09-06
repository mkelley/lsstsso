from logging import getLogger
from ..rsp import RSP


def lightcurve(
    rsp: RSP, ssobjectid: int, columns: list[str] | None = None, cached=True
):
    """Query the SSSource and DiaSource tables for photometry of an object.


    Parameters
    ----------
    ssobjectid : int
        The object ID.

    columns : list of str
        The columns to return.  SSSource columns may be prefixed with "s.",
        DiaSource columns may be prefixed with "d.", e.g., "s.ssObjectId".

    cached : bool, optional
        ``True`` to cache or return a cached query.


    Returns
    -------
    result : Result

    """

    logger = getLogger("lsstsso")
    logger.info("Querying SSSource INNER JOIN DiaSource")

    if columns is None:
        columns = [
            "s.SSObjectId",
            "d.midpointMjdTai",
            "d.ra",
            "d.dec",
            "s.helioRange",
            "s.topoRange",
            "s.phaseAngle",
            "s.elongation",
            "s.ephRate",
            "s.ephOffset",
            "d.band",
            "d.apFlux",
            "d.apFluxErr",
            "d.centroid_flag",
            "d.pixelFlags",
        ]

    query = (
        f"""
SELECT {",".join(columns)} FROM dp2.SSSource AS s
INNER JOIN dp2.DiaSource AS d on d.diaSourceId = s.diaSourceId
WHERE s.SSObjectId = {ssobjectid}
ORDER BY d.midpointMjdTai
""",
    )
    logger.debug(query)

    return rsp.query_tap(query, cached=cached)
