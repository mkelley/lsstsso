from dataclasses import dataclass
import astropy.units as u
from ..table import RSPTable


@dataclass
class SSObject(RSPTable):
    ssObjectId: int
    "Unique identifier."

    designation: str
    "The unpacked primary provisional designation for this object."

    nObs: int
    "Total number of LSST observations of this object."

    arc: u.Quantity[u.d]
    'Timespan ("arc") of all LSST observations, t_{last} - t_{first}'

    firstObservationMjdTai: u.Quantity[u.d]
    "The time of the first LSST observation of this object (could be precovered), TAI."

    MOIDEarth: u.Quantity[u.AU]
    "Minimum orbit intersection distance to Earth."

    MOIDEarthDeltaV: u.Quantity[u.km / u.s]
    "DeltaV at the MOID point."

    MOIDEarthEclipticLongitude: u.Quantity[u.deg]
    "Ecliptic longitude of the MOID point (Earth's orbit)."

    MOIDEarthTrueAnomaly: u.Quantity[u.deg]
    "True anomaly of the MOID point on Earth's orbit."

    MOIDEarthTrueAnomalyObject: u.Quantity[u.deg]
    "True anomaly of the MOID point on the object's orbit."

    tisserand_J: float
    "Tisserand parameter with respect to Jupiter (T_J)."

    extendednessMax: float
    "Maximum `extendedness` value from the DiaSource."

    extendednessMedian: float
    "Median `extendedness` value from the DiaSource."

    extendednessMin: float
    "Minimum `extendedness` value from the DiaSource."

    u_nObs: int
    "Total number of data points (u band)."

    u_H: u.Quantity[u.mag]
    "Best fit absolute magnitude (u band)."

    u_HErr: u.Quantity[u.mag]
    "Error in the estimate of H (u band)."

    u_G12: float
    "Best fit G12 slope parameter (u band)."

    u_G12Err: float
    "Error in the estimate of G12 (u band)."

    u_H_u_G12_Cov: u.Quantity[u.mag**2]
    "H–G12 covariance (u band)."

    u_nObsUsed: int
    "The number of data points used to fit the phase curve (u band)."

    u_Chi2: float
    "Chi^2 statistic of the phase curve fit (u band)."

    u_phaseAngleMin: u.Quantity[u.deg]
    "Minimum phase angle observed (u band)."

    u_phaseAngleMax: u.Quantity[u.deg]
    "Maximum phase angle observed (u band)."

    u_slope_fit_failed: bool
    "G12 fit failed in u band. G12 contains a fiducial value used to fit H."

    g_nObs: int
    "Total number of data points (g band)."

    g_H: u.Quantity[u.mag]
    "Best fit absolute magnitude (g band)."

    g_HErr: u.Quantity[u.mag]
    "Error in the estimate of H (g band)."

    g_G12: float
    "Best fit G12 slope parameter (g band)."

    g_G12Err: float
    "Error in the estimate of G12 (g band)."

    g_H_g_G12_Cov: u.Quantity[u.mag**2]
    "H–G12 covariance (g band)."

    g_nObsUsed: int
    "The number of data points used to fit the phase curve (g band)."

    g_Chi2: float
    "Chi^2 statistic of the phase curve fit (g band)."

    g_phaseAngleMin: u.Quantity[u.deg]
    "Minimum phase angle observed (g band)."

    g_phaseAngleMax: u.Quantity[u.deg]
    "Maximum phase angle observed (g band)."

    g_slope_fit_failed: bool
    "G12 fit failed in g band. G12 contains a fiducial value used to fit H."

    r_nObs: int
    "Total number of data points (r band)."

    r_H: u.Quantity[u.mag]
    "Best fit absolute magnitude (r band)."

    r_HErr: u.Quantity[u.mag]
    "Error in the estimate of H (r band)."

    r_G12: float
    "Best fit G12 slope parameter (r band)."

    r_G12Err: float
    "Error in the estimate of G12 (r band)."

    r_H_r_G12_Cov: u.Quantity[u.mag**2]
    "H–G12 covariance (r band)."

    r_nObsUsed: int
    "The number of data points used to fit the phase curve (r band)."

    r_Chi2: float
    "Chi^2 statistic of the phase curve fit (r band)."

    r_phaseAngleMin: u.Quantity[u.deg]
    "Minimum phase angle observed (r band)."

    r_phaseAngleMax: u.Quantity[u.deg]
    "Maximum phase angle observed (r band)."

    r_slope_fit_failed: bool
    "G12 fit failed in r band. G12 contains a fiducial value used to fit H."

    i_nObs: int
    "Total number of data points (i band)."

    i_H: u.Quantity[u.mag]
    "Best fit absolute magnitude (i band)."

    i_HErr: u.Quantity[u.mag]
    "Error in the estimate of H (i band)."

    i_G12: float
    "Best fit G12 slope parameter (i band)."

    i_G12Err: float
    "Error in the estimate of G12 (i band)."

    i_H_i_G12_Cov: u.Quantity[u.mag**2]
    "H–G12 covariance (i band)."

    i_nObsUsed: int
    "The number of data points used to fit the phase curve (i band)."

    i_Chi2: float
    "Chi^2 statistic of the phase curve fit (i band)."

    i_phaseAngleMin: u.Quantity[u.deg]
    "Minimum phase angle observed (i band)."

    i_phaseAngleMax: u.Quantity[u.deg]
    "Maximum phase angle observed (i band)."

    i_slope_fit_failed: bool
    "G12 fit failed in i band. G12 contains a fiducial value used to fit H."

    z_nObs: int
    "Total number of data points (z band)."

    z_H: u.Quantity[u.mag]
    "Best fit absolute magnitude (z band)."

    z_HErr: u.Quantity[u.mag]
    "Error in the estimate of H (z band)."

    z_G12: float
    "Best fit G12 slope parameter (z band)."

    z_G12Err: float
    "Error in the estimate of G12 (z band)."

    z_H_z_G12_Cov: u.Quantity[u.mag**2]
    "H–G12 covariance (z band)."

    z_nObsUsed: int
    "The number of data points used to fit the phase curve (z band)."

    z_Chi2: float
    "Chi^2 statistic of the phase curve fit (z band)."

    z_phaseAngleMin: u.Quantity[u.deg]
    "Minimum phase angle observed (z band)."

    z_phaseAngleMax: u.Quantity[u.deg]
    "Maximum phase angle observed (z band)."

    z_slope_fit_failed: bool
    "G12 fit failed in z band. G12 contains a fiducial value used to fit H."

    y_nObs: int
    "Total number of data points (y band)."

    y_H: u.Quantity[u.mag]
    "Best fit absolute magnitude (y band)."

    y_HErr: u.Quantity[u.mag]
    "Error in the estimate of H (y band)."

    y_G12: float
    "Best fit G12 slope parameter (y band)."

    y_G12Err: float
    "Error in the estimate of G12 (y band)."

    y_H_y_G12_Cov: u.Quantity[u.mag**2]
    "H–G12 covariance (y band)."

    y_nObsUsed: int
    "The number of data points used to fit the phase curve (y band)."

    y_Chi2: float
    "Chi^2 statistic of the phase curve fit (y band)."

    y_phaseAngleMin: u.Quantity[u.deg]
    "Minimum phase angle observed (y band)."

    y_phaseAngleMax: u.Quantity[u.deg]
    "Maximum phase angle observed (y band)."

    y_slope_fit_failed: bool
    "G12 fit failed in y band. G12 contains a fiducial value used to fit H."
