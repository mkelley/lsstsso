from dataclasses import dataclass, field
import astropy.units as u
from ..table import RSPTable


@dataclass
class SSSource(RSPTable):
    diaSourceId: int
    "Unique identifier of the observation (matching DiaSource.diaSourceId)."

    ssObjectId: int
    "Unique LSST identifier of the Solar System object."

    designation: str
    "The unpacked primary provisional designation for this object."

    eclLambda: u.Quantity[u.deg]
    "Ecliptic longitude, converted from the observed coordinates."

    eclBeta: u.Quantity[u.deg]
    "Ecliptic latitude, converted from the observed coordinates."

    galLon: u.Quantity[u.deg]
    "Galactic longitude, converted from the observed coordinates."

    galLat: u.Quantity[u.deg]
    "Galactic latitude, converted from the observed coordinates."

    elongation: u.Quantity[u.deg]
    "Solar elongation of the object at the time of observation."

    phaseAngle: u.Quantity[u.deg]
    "Phase angle between the Sun, object, and observer."

    topoRange: u.Quantity[u.au]
    "Topocentric distance (delta) at light-emission time."

    topoRangeRate: u.Quantity[u.km / u.s]
    "Topocentric radial (line-of-sight) velocity (deldot); positive values indicate motion away from the observer."

    helioRange: u.Quantity[u.au]
    "Heliocentric distance (r) at light-emission time."

    helioRangeRate: u.Quantity[u.km / u.s]
    "Heliocentric radial velocity (rdot); positive values indicate motion away from the Sun."

    ephRa: u.Quantity[u.deg]
    "Predicted ICRS right ascension from the orbit in mpc_orbits."

    ephDec: u.Quantity[u.deg]
    "Predicted ICRS declination from the orbit in mpc_orbits."

    ephVmag: u.Quantity[u.mag]
    "Predicted magnitude in V band, computed from mpc_orbits data including the mpc_orbits-provided (H, G) estimates"

    ephRate: u.Quantity[u.deg / u.d]
    "Total predicted on-sky angular rate of motion."

    ephRateRa: u.Quantity[u.deg / u.d]
    "Predicted on-sky angular rate in the R.A. direction (includes the cos(dec) factor)."

    ephRateDec: u.Quantity[u.deg / u.d]
    "Predicted on-sky angular rate in the declination direction."

    ephOffset: u.Quantity[u.arcsec]
    "Total observed versus predicted angular separation on the sky."

    ephOffsetRa: u.Quantity[u.arcsec]
    "Offset between observed and predicted position in the R.A. direction (includes cos(dec) term)."

    ephOffsetDec: u.Quantity[u.arcsec]
    "Offset between observed and predicted position in declination."

    ephOffsetAlongTrack: u.Quantity[u.arcsec]
    "Offset between observed and predicted position in the along-track direction on the sky."

    ephOffsetCrossTrack: u.Quantity[u.arcsec]
    "Offset between observed and predicted position in the cross-track direction on the sky."

    helio_x: u.Quantity[u.au]
    "Cartesian heliocentric X coordinate at light-emission time (ICRS)."

    helio_y: u.Quantity[u.au]
    "Cartesian heliocentric Y coordinate at light-emission time (ICRS)."

    helio_z: u.Quantity[u.au]
    "Cartesian heliocentric Z coordinate at light-emission time (ICRS)."

    helio_vx: u.Quantity[u.km / u.s]
    "Cartesian heliocentric X velocity at light-emission time (ICRS)."

    helio_vy: u.Quantity[u.km / u.s]
    "Cartesian heliocentric Y velocity at light-emission time (ICRS)."

    helio_vz: u.Quantity[u.km / u.s]
    "Cartesian heliocentric Z velocity at light-emission time (ICRS)."

    helio_vtot: u.Quantity[u.km / u.s]
    "The magnitude of the heliocentric velocity vector, sqrt(vx*vx + vy*vy + vz*vz)."

    topo_x: u.Quantity[u.au]
    "Cartesian topocentric X coordinate at light-emission time (ICRS)."

    topo_y: u.Quantity[u.au]
    "Cartesian topocentric Y coordinate at light-emission time (ICRS)."

    topo_z: u.Quantity[u.au]
    "Cartesian topocentric Z coordinate at light-emission time (ICRS)."

    topo_vx: u.Quantity[u.km / u.s]
    "Cartesian topocentric X velocity at light-emission time (ICRS)."

    topo_vy: u.Quantity[u.km / u.s]
    "Cartesian topocentric Y velocity at light-emission time (ICRS)."

    topo_vz: u.Quantity[u.km / u.s]
    "Cartesian topocentric Z velocity at light-emission time (ICRS)."

    topo_vtot: u.Quantity[u.km / u.s]
    "The magnitude of the topocentric velocity vector, sqrt(vx*vx + vy*vy + vz*vz)."

    diaDistanceRank: int
    "The rank of the diaSourceId-identified source in terms of its closeness to the predicted SSO position.  If diaSourceId is the nearest DiaSource to this SSO prediction, diaSourceDistanceRank=1 would be set.  If it is the second nearest, it would be 2, etc."
