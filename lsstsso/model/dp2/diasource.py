from dataclasses import dataclass
import astropy.units as u
from ..table import RSPTable


@dataclass
class DiaSource(RSPTable):
    diaSourceId: int
    "Unique identifier of this DiaSource."

    visit: int
    "Id of the visit where this diaSource was measured."

    detector: int
    "Id of the detector where this diaSource was measured."

    diaObjectId: int
    "Id of the diaObject this source was associated with, if any. If not, it is set to 0"

    ssObjectId: int
    "Id of the ssObject this source was associated with, if any. If not, it is set to 0"

    parentDiaSourceId: int
    "Id of the parent diaSource this diaSource has been deblended from, if any."

    midpointMjdTai: u.Quantity[u.d]
    "Effective mid-visit time for this diaSource, expressed as Modified Julian Date, International Atomic Time."

    ra: u.Quantity[u.deg]
    "Right ascension coordinate of the center of this diaSource."

    dec: u.Quantity[u.deg]
    "Declination coordinate of the center of this diaSource."

    raErr: u.Quantity[u.deg]
    "Angular error in right ascension (∂RA*cos(Dec))."

    decErr: u.Quantity[u.deg]
    "Error in declination."

    ra_dec_Cov: u.Quantity[u.deg**2]
    "Covariance between right ascension (RA*cos(Dec)) and declination."

    x: u.Quantity[u.pixel]
    "Unweighted first moment centroid, overall centroid."

    xErr: u.Quantity[u.pixel]
    "1-sigma uncertainty on x position."

    y: u.Quantity[u.pixel]
    "Unweighted first moment centroid, overall centroid."

    yErr: u.Quantity[u.pixel]
    "1-sigma uncertainty on y position."

    centroid_flag: bool
    "General centroid algorithm failure flag; set if anything went wrong when fitting the centroid. Another centroid flag field should also be set to provide more information."

    apFlux: u.Quantity[u.nJy]
    "Flux in a 12 pixel radius aperture on the difference image."

    apFluxErr: u.Quantity[u.nJy]
    "Estimated uncertainty of apFlux."

    apFlux_flag: bool
    "General aperture flux algorithm failure flag; set if anything went wrong when measuring aperture fluxes. Another apFlux flag field should also be set to provide more information."

    apFlux_flag_apertureTruncated: bool
    "Aperture did not fit within measurement image."

    isNegative: bool
    "Source was detected as significantly negative."

    snr: float
    "The signal-to-noise ratio at which this source was detected in the difference image."

    psfFlux: u.Quantity[u.nJy]
    "Flux for Point Source model. Note this actually measures the flux difference between the template and the visit image."

    psfFluxErr: u.Quantity[u.nJy]
    "Uncertainty of psfFlux."

    psfChi2: float
    "Chi^2 statistic of the point source model fit."

    psfNdata: u.Quantity[u.pixel]
    "The number of data points (pixels) used to fit the point source model."

    psfFlux_flag: bool
    "Failure to derive linear least-squares fit of psf model. Another psfFlux flag field should also be set to provide more information."

    psfFlux_flag_edge: bool
    "Object was too close to the edge of the image to use the full PSF model."

    psfFlux_flag_noGoodPixels: bool
    "Not enough non-rejected pixels in data to attempt the fit."

    trailFlux: u.Quantity[u.nJy]
    "Flux for a trailed source model. Note this actually measures the flux difference between the template and the visit image."

    trailFluxErr: u.Quantity[u.nJy]
    "Uncertainty of trailFlux."

    trailRa: u.Quantity[u.deg]
    "Right ascension coordinate of centroid for trailed source model."

    trailDec: u.Quantity[u.deg]
    "Declination coordinate of centroid for trailed source model."

    trailLength: u.Quantity[u.arcsec]
    "Maximum likelihood fit of trail length."

    trailAngle: u.Quantity[u.deg]
    "Maximum likelihood fit of the angle between the meridian through the centroid and the trail direction (bearing)."

    trail_flag_edge: bool
    "This flag is set if a trailed source extends onto or past edge pixels."

    dipoleMeanFlux: u.Quantity[u.nJy]
    "Maximum likelihood value for the mean absolute flux of the two lobes for a dipole model."

    dipoleMeanFluxErr: u.Quantity[u.nJy]
    "Uncertainty of dipoleMeanFlux."

    dipoleFluxDiff: u.Quantity[u.nJy]
    "Maximum likelihood value for the difference of absolute fluxes of the two lobes for a dipole model."

    dipoleFluxDiffErr: u.Quantity[u.nJy]
    "Uncertainty of dipoleFluxDiff."

    dipoleLength: u.Quantity[u.arcsec]
    "Maximum likelihood value for the lobe separation in dipole model."

    dipoleAngle: u.Quantity[u.deg]
    "Maximum likelihood fit of the angle between the meridian through the centroid and the dipole direction (bearing, from negative to positive lobe)."

    dipoleChi2: float
    "Chi^2 statistic of the model fit."

    dipoleNdata: int
    "The number of data points (pixels) used to fit the model."

    scienceFlux: u.Quantity[u.nJy]
    "Forced photometry flux for a point source model measured on the visit image centered at DiaSource position."

    scienceFluxErr: u.Quantity[u.nJy]
    "Estimated uncertainty of scienceFlux."

    forced_PsfFlux_flag: bool
    "Forced PSF photometry on science image failed. Another forced_PsfFlux flag field should also be set to provide more information."

    forced_PsfFlux_flag_edge: bool
    "Forced PSF flux on science image was too close to the edge of the image to use the full PSF model."

    forced_PsfFlux_flag_noGoodPixels: bool
    "Forced PSF flux not enough non-rejected pixels in data to attempt the fit."

    templateFlux: u.Quantity[u.nJy]
    "Forced photometry flux for a point source model measured on the template image centered at the DiaSource position."

    templateFluxErr: u.Quantity[u.nJy]
    "Uncertainty of templateFlux."

    ixx: u.Quantity[u.nJy * u.arcsec**2]
    "Adaptive second moment of the source intensity."

    iyy: u.Quantity[u.nJy * u.arcsec**2]
    "Adaptive second moment of the source intensity."

    ixy: u.Quantity[u.nJy * u.arcsec**2]
    "Adaptive second moment of the source intensity."

    ixxPSF: u.Quantity[u.nJy * u.arcsec**2]
    "Adaptive second moment for the PSF."

    iyyPSF: u.Quantity[u.nJy * u.arcsec**2]
    "Adaptive second moment for the PSF."

    ixyPSF: u.Quantity[u.nJy * u.arcsec**2]
    "Adaptive second moment for the PSF."

    shape_flag: bool
    "General source shape algorithm failure flag; set if anything went wrong when measuring the shape. Another shape flag field should also be set to provide more information."

    shape_flag_no_pixels: bool
    "No pixels to measure shape."

    shape_flag_not_contained: bool
    "Center not contained in footprint bounding box."

    shape_flag_parent_source: bool
    "This source is a parent source; we should only be measuring on deblended children in difference imaging."

    extendedness: float
    "A measure of extendedness, computed by comparing an object's moment-based trace radius to the PSF moments. extendedness = 1 implies a high degree of confidence that the source is extended. extendedness = 0 implies a high degree of confidence that the source is point-like."

    reliability: float
    "Probability (0-1) that the diaSource is astrophysical, derived from a machine learning model."

    band: str
    "Filter band this source was observed with."

    isDipole: bool
    "Source well fit by a dipole."

    dipoleFitAttempted: bool
    "Attempted to fit a dipole model to this source."

    timeProcessedMjdTai: float
    "Time when the image was processed and this DiaSource record was generated, expressed as Modified Julian Date, International Atomic Time."

    bboxSize: u.Quantity[u.pixel]
    "Size of the square bounding box that fully contains the detection footprint."

    pixelFlags: bool
    "General pixel flags failure; set if anything went wrong when setting pixels flags from this footprint's mask. This implies that some pixelFlags for this source may be incorrectly set to False."

    pixelFlags_bad: bool
    "Bad pixel in the DiaSource footprint."

    pixelFlags_cr: bool
    "Cosmic ray in the DiaSource footprint."

    pixelFlags_crCenter: bool
    "Cosmic ray in the 3x3 region around the centroid."

    pixelFlags_edge: bool
    "Some of the source footprint is outside usable exposure region (masked EDGE or centroid off image)."

    pixelFlags_nodata: bool
    "NO_DATA pixel in the source footprint."

    pixelFlags_nodataCenter: bool
    "NO_DATA pixel in the 3x3 region around the centroid."

    pixelFlags_interpolated: bool
    "Interpolated pixel in the DiaSource footprint."

    pixelFlags_interpolatedCenter: bool
    "Interpolated pixel in the 3x3 region around the centroid."

    pixelFlags_offimage: bool
    "DiaSource center is off image."

    pixelFlags_saturated: bool
    "Saturated pixel in the DiaSource footprint."

    pixelFlags_saturatedCenter: bool
    "Saturated pixel in the 3x3 region around the centroid."

    pixelFlags_suspect: bool
    "DiaSource's footprint includes suspect pixels."

    pixelFlags_suspectCenter: bool
    "Suspect pixel in the 3x3 region around the centroid."

    pixelFlags_streak: bool
    "Streak in the DiaSource footprint."

    pixelFlags_streakCenter: bool
    "Streak in the 3x3 region around the centroid."

    pixelFlags_injected: bool
    "Injection in the DiaSource footprint."

    pixelFlags_injectedCenter: bool
    "Injection in the 3x3 region around the centroid."

    pixelFlags_injected_template: bool
    "Template injection in the DiaSource footprint."

    pixelFlags_injected_templateCenter: bool
    "Template injection in the 3x3 region around the centroid."

    glint_trail: bool
    "This flag is set if the source is part of a glint trail."
