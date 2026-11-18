"""

The color transformation matrix can be visualized as:

          u   g   r   i   z   y
    u |   0 u-g u-r u-i u-z u-y |
    g | g-u   0 g-r g-i g-z g-y |
    r | r-u r-g   0 r-i r-z r-y |
    i | i-u i-g i-r   0 i-z i-y |
    z | z-u z-g z-r z-i   0 z-y |
    y | y-u y-g y-r y-i y-z   0 |

Internally, it is a 15-element array for each of the upper triangle elements,
excluding the main diagonal.

"""

from collections.abc import Iterator
from itertools import combinations

import astropy.units as u
import numpy as np
from numpy.ma import MaskedArray

from ..band import Band
from .color import Color
from .transform import transform


class ColorMatrix:
    """Color transformation matrix.

    Use this class to convert between colors.


    Parameters
    ----------
    index : array, optional
        A length-15 array of the measured color indices (units of mag) in the
        following order: u-g, u-r, u-i, u-z, u-y, g-r, g-i, etc.

    unc : array, optional
        A length-15 array of the uncertainties on each element of ``colors`` or
        a 15x15 element covariance matrix.


    Examples
    --------
    >>> import astropy.units as u
    >>> from lsstsso import Band, Color, ColorMatrix
    >>>
    >>> colors = [
    ...     Color(Band.u, Band.g, 1.0, 0.1),
    ...     Color(Band.g, Band.i, 1.3, 0.1),
    ...     Color(Band.r, Band.i, 0.2, 0.05),
    ... ]
    >>> cm = ColorMatrix.from_colors(colors)
    >>> print(cm)
    u-g = 1.000 ± 0.100 mag
    g-i = 1.300 ± 0.100 mag
    r-i = 0.200 ± 0.050 mag
    >>> print(cm.transform(0 * u.mag, 0.03 * u.mag, Band.u, Band.g))
    (<Quantity -1. mag>, <Quantity 0.10440307 mag>)

    The uncertainties are internally stored as a covariance matrix:

    >>> print(cm.cov)

    As a convenience, the 1-sigma uncertainties are accessible via the ``unc``
    attribute:

    >>> print(cm.unc)

    """

    def __init__(self, index: np.ndarray | None = None, unc: np.ndarray | None = None):
        if index is None:
            self.index = MaskedArray(np.zeros(15), masked=np.ones(15, bool))
        elif np.shape(index) != (15,):
            raise ValueError("index must have length 15")
        else:
            self.index = MaskedArray(index)

        if unc is None:
            self.cov = MaskedArray(np.zeros((15, 15)), masked=np.ones((15, 15), bool))
        elif np.shape(unc) == (15,):
            self.cov = np.ma.diag(unc**2)
        elif np.shape(unc) == (15, 15):
            self.cov = MaskedArray(unc)
        else:
            raise ValueError("index must have length 15 or shape (15, 15)")

    @classmethod
    def from_colors(cls, colors: list[Color]) -> "ColorMatrix":
        """Initialize from a list of |Color| objects.


        Parameters
        ----------
        colors : list of Color
            The colors to consider.  Avoid repeating colors, but if a single
            color has multiple measurements, they will be weighted and averaged.


        Returns
        -------
        cm : ColorMatrix

        """

        index = MaskedArray(np.zeros(15), mask=np.ones(15, bool))
        unc = MaskedArray(np.zeros(15), mask=np.ones(15, bool))

        for color in colors:
            if color.left < color.right:
                blue = color.left
                red = color.right
                scale = 1
            else:
                blue = color.right
                red = color.left
                scale = -1

            i = cls.bands_to_array_index(blue, red)
            avg = color.mean()
            index[i] = scale * avg.index.value
            unc[i] = avg.unc.value

        return ColorMatrix(index, unc)

    @property
    def unc(self) -> MaskedArray:
        return np.sqrt(np.ma.diag(self.cov))

    def __repr__(self):
        return f"<ColorMatrix: {len(self)} values>"

    def __str__(self):
        lines = []
        for color in self:
            lines.append(str(color))

        return "\n".join(lines)

    def __len__(self):
        """Number of independent and unmasked colors."""
        return np.sum(~self.index.mask)

    @staticmethod
    def bands_to_array_index(blue: Band | str, red: Band | str) -> int:
        """Get the array index corresponding to the blue-red color.


        Parameters
        ----------
        blue, red : |Band| or str
            The bands for the blue-red color.


        Returns
        -------
        i : int
            The array index that corresponds to this color.

        """

        return list(combinations(Band, 2)).index((blue, red))

    @staticmethod
    def array_index_to_bands(i: int) -> tuple[Band, Band]:
        """Get the color corresponding to this array index.


        Parameters
        ----------
        i : int
            The array index that corresponds to this color.


        Returns
        -------
        blue, red : |Band|
            The bands for the blue-red color.

        """

        return list(combinations(Band, 2))[i]

    def __getitem__(self, bands: tuple[Band | str, Band | str]) -> Color:
        """a - b color.


        Parameters
        ----------
        left, right : |Band| or str


        Returns
        -------
        color : |Color|
            The left-right color.

        """

        a, b = bands
        i = self.bands_to_array_index(a, b)

        scale = 1
        if a > b:
            b, a = a, b
            scale = -1

        return Color(a, b, scale * self.index[i], self.unc[i])

    def __iter__(self) -> Iterator[Color]:
        """Iterate over the unmasked colors."""
        for i in range(15):
            if self.index.mask[i]:
                continue
            left, right = self.array_index_to_bands(i)
            yield Color(left, right, self.index[i], self.unc[i])

    def transform(
        self,
        m: u.Quantity,
        unc: u.Quantity,
        from_band: Band | str,
        to_band: Band | str,
    ) -> tuple[u.Quantity, u.Quantity]:
        """Transform a measurement in one band to another.


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


        Results
        -------
        m_t : u.Quantity
            The transformed measurement.

        unc_t : u.Quantity
            The uncertainty on ``m_t``.


        Raises
        ------
        ValueError
            If the transformation between these bands is not possible.

        """

        return transform(m, unc, from_band, to_band, self)
