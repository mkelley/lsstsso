from .ssobject import ssobject
from ..result import ResultClass


def comets(columns: list[str] | None = None, cached=True) -> ResultClass:
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
    return ssobject(constraints, columns=columns, cached=cached)
