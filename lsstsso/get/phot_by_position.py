from logging import getLogger
import astropy.units as u
from astropy.coordinates import SkyCoord
from ..expect import expect
from ..rsp import RSP


def phot_by_position(
    rsp: RSP,
    coords: SkyCoord,
    tolerance: u.Quantity = 1 * u.arcsec,
    table: str = "DiaSource",
    constraints: str | None = None,
    columns: list[str] | None = None,
    cached=True,
):
    """Query the Source or DiaSource tables for photometry near coordinates.


    Parameters
    ----------

    coords : Table
        The coordinates to query as columns "ra" and "dec".  An additional
        "objid" column is optional.  If it exists, it will be automatically
        returned when ``columns`` is ``None``. Other columns may be added and
        used in the query.  The table will be uploaded as "coords".

    tolerance : Quantity
        Query for photometry within ``tolerance`` of ``coords``.

    table : str
        The table to query: Source or DiaSource

    constraints : str, optional
        Other coords constraints.

    columns : list of str
        The columns to return.  The user table columns may be prefixed with
        "coords." and the Source/DiaSource table may be prefixed with "source.",
        e.g., "source.midpointMjdTai", "coords.objid".

    cached : bool, optional
        ``True`` to cache or return a cached coords.


    Returns
    -------
    result : Result

    """

    expect(table in ["Source", "DiaSource"], ValueError(f"Invalid table: {table}"))

    logger = getLogger("lsstsso")
    logger.info(
        f"Querying {table} for {len(coords)} user coordinates within {tolerance}"
    )

    if columns is None:
        columns = ["coords.objid AS query_objid"] if "objid" in coords.columns else []
        columns += [
            "coords.ra AS query_ra",
            "coords.dec AS query_dec",
            "source.ra AS source_ra",
            "source.dec AS source_dec",
            "source.midpointMjdTai",
            "source.band",
            "source.apFlux",
            "source.apFluxErr",
            "source.centroid_flag",
            "source.pixelFlags",
        ]

    query = f"""
    SELECT {",".join(columns)}
    FROM dp2.{table} AS source
    JOIN TAP_UPLOAD.coords AS coords
    ON DISTANCE(POINT('ICRS', source.ra, source.dec),
                POINT('ICRS', coords.ra, coords.dec)) < {tolerance.to_value(u.deg)}
    """
    if constraints is not None:
        query += "WHERE " + constraints

    logger.debug(query)

    return rsp.query_tap(
        query,
        uploads={"coords": coords},
        cached=cached,
        units={"query_ra": "deg", "query_dec": "deg"},
    )
