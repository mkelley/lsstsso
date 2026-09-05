from logging import getLogger
from .rsp import RSP


def ssobject(rsp: RSP, constraints: str, columns: list[str] | None = None, cached=True):
    """Query the SSObject and numbered_identifications tables.


    Parameters
    ----------
    constraints : str
        The query constraints.


    Returns
    -------
    result

    """

    logger = getLogger()
    logger.info("Querying SSObject on the RSP")

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
ON unpacked_primary_provisional_designation = designation
WHERE {constraints}
"""
    logger.debug(query)

    result = rsp.query_tap(query, cached=cached)

    return result


def comets(rsp: RSP, columns: list[str] | None = None, cached=True):
    """Get a list of all SSObjects with cometary designations."""

    constraints = (
        "designation LIKE 'C/%' OR designation LIKE 'P/%' OR designation LIKE 'A/%'"
    )
    return ssobject(rsp, constraints, columns=columns, cached=cached)


def lightcurve(
    rsp: RSP, ssobjectid: int, columns: list[str] | None = None, cached=True
):
    """Get an SSObject's lightcurve.

    The query joins the SSSource and DiaSource tables.


    Parameters
    ----------
    ssobjectid : int
        The object ID.


    Returns
    -------
    result

    """

    logger = getLogger()
    logger.info("Querying SSSource/DiaSource on the RSP")

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

    result = rsp.query_tap(
        f"""
SELECT {",".join(columns)} FROM dp2.SSSource AS s
INNER JOIN dp2.DiaSource AS d on d.diaSourceId = s.diaSourceId
WHERE s.SSObjectId = {ssobjectid}
ORDER BY d.midpointMjdTai
""",
        cached=cached,
    )

    return result


def orbit(rsp: RSP, designation: str, columns: list[str] | None = None, cached=True):
    """Get an SSObject's orbit."""

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

    result = rsp.query_tap(
        f"""
SELECT {",".join(columns)} FROM dp2.mpc_orbits
WHERE designation = '{designation}'
""",
        cached=cached,
    )

    return result
