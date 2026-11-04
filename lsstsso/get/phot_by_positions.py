from logging import getLogger

import astropy.units as u
from astropy.coordinates import SkyCoord

from .. import rsp
from ..result import Result

source_default_columns = [
    "ra",
    "dec",
    "band",
    "visit",
    "detector",
    "sourceId",
    "psfFlux",
    "psfFluxErr",
    "psfFlux_flag",
    "ap12Flux",
    "ap12FluxErr",
    "ap12Flux_flag",
    "ap17Flux",
    "ap17FluxErr",
    "ap17Flux_flag",
    "ap25Flux",
    "ap25FluxErr",
    "ap25Flux_flag",
    "ixx",
    "iyy",
    "ixxPSF",
    "iyyPSF",
    "centroid_flag",
    "reliability",
    "extendedness",
]

diaSource_default_columns = [
    "ra",
    "dec",
    "band",
    "diaSourceId",
    "ssObjectId",
    "midpointMjdTai",
    "psfFlux",
    "psfFluxErr",
    "psfFlux_flag",
    "trailFlux",
    "trailFluxErr",
    "trailLength",
    "trailAngle",
    "apFlux",
    "apFluxErr",
    "apFlux_flag",
    "ixx",
    "iyy",
    "ixxPSF",
    "iyyPSF",
    "centroid_flag",
    "reliability",
    "extendedness",
]


def phot_by_positions(
    query: SkyCoord,
    tolerance: u.Quantity = 1 * u.arcsec,
    table: str = "DiaSource",
    constraints: str | None = None,
    columns: list[str] | None = None,
    cache=True,
) -> Result:
    """Query the Source or DiaSource tables for photometry near coordinates.


    Parameters
    ----------
    query : Table
        The coordinates to query as columns "ra" and "dec".  An additional
        "objid" column is optional.  If it exists, it will be automatically
        returned when ``columns`` is ``None``. Other columns may be added and
        used in the query.

    tolerance : Quantity
        Query for photometry within an angular cone of radius ``tolerance``.

    table : str
        The table to query: "Source" or "DiaSource"

    constraints : str, optional
        Other query constraints.  See Notes.

    columns : list of str, optional
        The columns to return.  See Notes.

    cached : bool, optional
        ``True`` to cache or return a cached query.


    Returns
    -------
    result : Result


    Notes
    -----
    Within the ADQL command, the user table is named "query" and the
    Source/DiaSource table is named "source", e.g., "source.midpointMjdTai",
    "query.objid".

    """

    if table not in ["Source", "DiaSource"]:
        raise ValueError(f"Invalid table: {table}")

    logger = getLogger("lsstsso")
    logger.info(
        f"Querying {table} for {len(query)} user coordinates within {tolerance}"
    )

    if columns is None:
        columns = ["query.objid AS query_objid"] if "objid" in query.columns else []
        columns += [
            "query.ra AS query_ra",
            "query.dec AS query_dec",
        ]

        if table == "Source":
            default_columns = source_default_columns
        else:
            default_columns = diaSource_default_columns

        columns += [f"source.{col}" for col in default_columns]

    cmd = f"""
    SELECT {",".join(columns)}
    FROM dp2.{table} AS source
    JOIN TAP_UPLOAD.query AS query
    ON DISTANCE(POINT('ICRS', source.ra, source.dec),
                POINT('ICRS', query.ra, query.dec)) < {tolerance.to_value(u.deg)}
    """
    if constraints is not None:
        cmd += "WHERE " + constraints

    logger.debug(query)

    with rsp.provider() as _rsp:
        return _rsp.query_tap(cmd, uploads={"query": query}, cache=cache)
