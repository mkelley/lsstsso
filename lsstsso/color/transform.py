import typing

import astropy.units as u
import numpy as np

from ..band import Band

if typing.TYPE_CHECKING:
    from .color_matrix import ColorMatrix


def transform(
    m: u.Quantity,
    unc: u.Quantity,
    from_band: Band | str | list[Band | str],
    to_band: Band | str,
    cm: "ColorMatrix",
) -> tuple[u.Quantity, u.Quantity]:
    """Transform a band to another.


    Parameters
    ----------
    m : u.Quantity
        The observation(s) to transform in units of magnitudes.

    unc : u.Quantity
        The uncertainty on ``m``.

    from_band : Band or str or array thereof
        The band(s) in which ``m`` is measured.

    to_band : Band or str
        The band to transform to.

    cm : ColorMatrix
        The color transformation matrix.


    Results
    -------
    m_t : u.Quantity or "MaskedQuantity"
        The transformed measurement(s).  Masks will be used for values that
        cannot be calculated with ``cm``.

    unc_t : u.Quantity
        The uncertainty on ``m_t``.

    """

    n = np.size(m)
    _m = u.Quantity(m, u.mag).reshape((n,))
    _unc = u.Quantity(unc, u.mag).reshape((n,))

    m_t = np.ma.zeros_like(_m)
    m_t.mask = True
    unc_t = np.ma.zeros_like(_m)
    unc_t.mask = True

    bands = np.array(from_band).reshape((np.size(from_band),))
    for band in set(bands):
        color = cm[band, to_band]
        if color is None:
            continue

        i = bands == band
        m_t[i] = _m[i] - color.index
        unc_t[i] = np.hypot(_unc[i], color.unc)

    if not any(m_t.mask):
        m_t = m_t.data
        unc_t = unc_t.data

    return m_t.reshape(m.shape), unc_t.reshape(m.shape)
