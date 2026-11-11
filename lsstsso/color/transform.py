import astropy.units as u
import numpy as np

from ..band import Band
from .color_matrix import ColorMatrix


def transform(
    m: u.Quantity,
    unc: u.Quantity,
    from_band: Band | str,
    to_band: Band | str,
    color_matrix: ColorMatrix,
) -> tuple[u.Quantity, u.Quantity]:
    """Transform a band to another.


    Parameters
    ----------
    m : u.Quantity
        The observation to transform in units of magnitudes.

    unc : u.Quantity
        The uncertainty on ``m``.

    from_band : Band or str
        The band in which ``m`` is measured.

    to_band : Band or str
        The band to transform to.

    color_matrix : ColorMatrix
        The color transformation matrix.


    Results
    -------
    m_t : u.Quantity
        The transformed measurement.

    unc_t : u.Quantity
        The uncertainty on ``m_t``.


    Raises
    ------
    ValueError
        If the transformation between these bands is not possible with
        ``color_matrix``.

    """

    color = color_matrix[from_band, to_band]
    if color is np.ma.masked:
        raise ValueError(f"Missing color transformation for {from_band} to {to_band}.")

    m_t = u.Quantity(m, u.mag) - color.index
    unc_t = np.hypot(u.Quantity(unc, u.mag), color.unc)

    return m_t, unc_t
