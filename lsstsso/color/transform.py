import typing

import astropy.units as u
import numpy as np
from astropy.utils.masked import Masked

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
    m_t : MaskedQuantity
        The transformed measurement(s).  Masks will be used for values that
        cannot be calculated with ``cm``.

    unc_t : MaskedQuantity
        The uncertainty on ``m_t``.

    """

    n = np.size(m)
    _m = u.Quantity(m, u.mag).reshape((n,))
    _unc = u.Quantity(unc, u.mag).reshape((n,))

    if np.size(from_band) != n:
        # assume it is a single value
        bands = np.repeat(from_band, n).reshape((n,))
    else:
        bands = np.array(from_band).reshape((n,))

    m_t = Masked(_m, mask=True)
    unc_t = Masked(_unc, mask=True)

    for band in set(bands):
        color = cm[band, to_band]
        if color is None:
            continue

        i = bands == band
        m_t[i] = _m[i] - color.index
        unc_t[i] = np.hypot(_unc[i], color.unc)

    # m_t.reshape(()) and m_t.squeeze() can result in a weird object that can't
    # be printed: "*** AttributeError: '_MaskedPrintOption' object has no
    # attribute 'size'""
    if m.shape == ():
        return m_t[0], unc_t[0]

    return m_t.reshape(m.shape), unc_t.reshape(m.shape)
