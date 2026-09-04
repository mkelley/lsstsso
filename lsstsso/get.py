from .model.dp2 import SSObject
from .rsp import RSP


def ssobjects(rsp: RSP, constraints: str, cached=True):
    """Get an SSObject's lightcurve.


    Parameters
    ----------
    constraints : str
        The query constraints.


    Returns
    -------
    result

    """

    result = rsp.query_tap(
        "SELECT * FROM dp2.SSObject WHERE {contraints}", cached=cached
    )

    return result


def comets(rsp: RSP, columns: list[str] | None = None, cached=True):
    """Get a list of all SSObjects with cometary designations."""

    if columns is None:
        columns = [
            "ssObjectId",
            "designation",
            "nObs",
            "arc",
            "firstObservationMjdTai",
            "tisserand_J",
        ]

    result = rsp.query_tap(
        f"""
SELECT {",".join(columns)} FROM dp2.SSObject
WHERE designation LIKE 'C/%' OR designation LIKE 'P/%' OR designation LIKE 'A/%'
ORDER BY nObs
""",
        cached=cached,
    )

    return result


def lightcurve(rsp: RSP, ssobject: SSObject, cached=True):
    """Get an SSObject's lightcurve.


    Parameters
    ----------
    ssobject : SSObject
        The object to query.


    Returns
    -------
    result

    """

    result = rsp.query_tap(
        f"""
SELECT * FROM dp2.SSSource AS s
INNER JOIN dp2.DiaSource AS d on d.diaSourceId = s.diaSourceId
WHERE s.SSObjectId = {ssobject.ssObjectId}
ORDER BY d.midpointMjdTai
""",
        cached=cached,
    )

    return result
