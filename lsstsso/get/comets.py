from .ssobject import ssobject
from ..rsp import RSP


def comets(rsp: RSP, columns: list[str] | None = None, cached=True):
    """Get a list of all SSObjects with cometary designations.


    Parameters
    ----------
    columns : list of str
        The columns to return.  SSObject columns may be prefixed with "s.",
        numbered_identifications may be prefixed with "n.", e.g.,
        "s.ssObjectId".

    cached : bool, optional
        ``True`` to cache or return a cached query.


    Returns
    -------
    result : Result

    """

    constraints = "s.designation LIKE 'C/%' OR s.designation LIKE 'P/%' OR s.designation LIKE 'A/%'"
    return ssobject(rsp, constraints, columns=columns, cached=cached)
