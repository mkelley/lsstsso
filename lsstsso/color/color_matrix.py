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
from astropy.table import Table
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
        A length-15 array of the 1-sigma uncertainties on each element of
        ``colors`` or a 15x15 element covariance matrix.


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

    >>> print(cm.cov)  # doctest: +FLOAT_CMP
    [[0.010000000000000002 -- -- -- -- -- -- -- -- -- -- -- -- -- --]
     [-- -- -- -- -- -- -- -- -- -- -- -- -- -- --]
     [-- -- -- -- -- -- -- -- -- -- -- -- -- -- --]
     [-- -- -- -- -- -- -- -- -- -- -- -- -- -- --]
     [-- -- -- -- -- -- -- -- -- -- -- -- -- -- --]
     [-- -- -- -- -- -- -- -- -- -- -- -- -- -- --]
     [-- -- -- -- -- -- 0.010000000000000002 -- -- -- -- -- -- -- --]
     [-- -- -- -- -- -- -- -- -- -- -- -- -- -- --]
     [-- -- -- -- -- -- -- -- -- -- -- -- -- -- --]
     [-- -- -- -- -- -- -- -- -- 0.0025000000000000005 -- -- -- -- --]
     [-- -- -- -- -- -- -- -- -- -- -- -- -- -- --]
     [-- -- -- -- -- -- -- -- -- -- -- -- -- -- --]
     [-- -- -- -- -- -- -- -- -- -- -- -- -- -- --]
     [-- -- -- -- -- -- -- -- -- -- -- -- -- -- --]
     [-- -- -- -- -- -- -- -- -- -- -- -- -- -- --]]

    As a convenience, the 1-sigma uncertainties are accessible via the ``unc``
    attribute:

    >>> print(cm.unc)
    [0.1 -- -- -- -- -- 0.1 -- -- 0.05 -- -- -- -- --]

    """

    def __init__(self, index: np.ndarray | None = None, unc: np.ndarray | None = None):
        if index is None:
            index = MaskedArray(np.zeros(15), mask=np.ones(15, bool))
        if unc is None:
            unc = MaskedArray(np.zeros((15, 15)), mask=np.ones((15, 15), bool))

        if np.shape(index) != (15,):
            raise ValueError("index must have length 15")

        self.index = MaskedArray(index)

        if np.shape(unc) == (15,):
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
            The colors to consider.  Avoid repeating colors.  If a single
            |Color| object has multiple measurements, then they will be
            averaged.


        Returns
        -------
        cm : ColorMatrix

        """

        cm = ColorMatrix()
        for color in colors:
            cm.set(color.mean())

        return cm

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

    def __iter__(self) -> Iterator[Color]:
        """Iterate over the unmasked colors."""
        for i in range(15):
            if self.index.mask[i]:
                continue
            left, right = self.array_index_to_bands(i)
            yield Color(left, right, self.index[i], self.unc[i])

    def __getitem__(self, bands: tuple[Band | str, Band | str]) -> Color | None:
        """a - b color.


        Parameters
        ----------
        left, right : |Band| or str


        Returns
        -------
        color : |Color| or None
            The left-right color or ``None`` if this color is not defined.

        """

        a, b = [Band(b) for b in bands]

        if a == b:
            return Color(a, b, 0 * u.mag, 0 * u.mag)

        scale = 1
        if a > b:
            b, a = a, b
            scale = -1

        i = self.bands_to_array_index(a, b)
        if self.index[i] is np.ma.masked:
            return None

        return Color(a, b, scale * self.index[i], self.unc[i])

    def __setitem__(
        self,
        bands: tuple[Band | str, Band | str],
        value: tuple[u.Quantity, u.Quantity],
    ) -> None:
        """Set a - b color.


        Parameters
        ----------
        bands : tuple of |Band| or str
            The color to set: ``bands[0] - bands[1]``.

        value : tuple of |Quantity|
            The value and uncertainty.


        Examples
        --------
        >>> from lsstsso.color import ColorMatrix
        >>> cm = ColorMatrix()
        >>> cm["g", "r"] = 0.4 * u.mag, 0.01 * u.mag

        """

        a, b = [Band(b) for b in bands]
        value = [
            x if x is np.ma.masked else u.Quantity(x, u.mag).to_value("mag")
            for x in value
        ]

        scale = 1
        if a > b:
            b, a = a, b
            scale = -1

        i = self.bands_to_array_index(a, b)
        self.index[i] = scale * value[0]
        self.cov[i, i] = value[1] ** 2

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

    def set(self, color: Color) -> None:
        """Set a color.


        Parameters
        ----------
        color : Color

        """

        self[color.left, color.right] = color.index, color.unc

    def covariance(self, color1: list[Band | str], color2: list[Band | str]) -> float:
        """Get the covariance between two colors.


        Parameters
        ----------
        color1, color2 : list of Band or str
            Each color is a ``[blue, red]`` pair of bands depicting the ``blue -
            red`` color.


        Returns
        -------
        cov : float or `numpy.ma.masked`
            The covariance between the two colors, or a masked value if it does
            not exist.

        """

        i = self.bands_to_array_index(*color1)
        j = self.bands_to_array_index(*color2)
        return self.cov[i, j]

    def transform(
        self,
        m: u.Quantity,
        unc: u.Quantity,
        from_band: Band | str | list[Band | str],
        to_band: Band | str,
    ) -> tuple[u.Quantity, u.Quantity]:
        """Transform a measurement in one band to another.


        Parameters
        ----------
        m : u.Quantity
            The observation(s) to transform in units of magnitudes.

        unc : u.Quantity
            The uncertainty on ``m``.

        from_band : Band or str, or array thereof
            The band(s) in which ``m`` is measured.

        to_band : Band or str
            The band to transform to.


        Results
        -------
        m_t : u.Quantity
            The transformed measurement(s).

        unc_t : u.Quantity
            The uncertainty on ``m_t``.


        Raises
        ------
        ValueError
            If the transformation between these bands is not possible.

        """

        return transform(m, unc, from_band, to_band, self)

    @classmethod
    def read(cls, fn: str) -> "ColorMatrix":
        """Read a previously saved color matrix file.


        Parameters
        ----------
        fn : str
            File name.

        """

        tab = Table.read(fn, format="ascii.ecsv")
        index = []
        cov = []
        for row in tab:
            index.append(row["index"])
            mask = [value is np.ma.masked for value in list(row)[2:]]
            data = [0 if value is np.ma.masked else value for value in list(row)[2:]]
            cov.append(np.ma.masked_array(data, mask=mask))

        index = np.ma.masked_array(
            [0 if value is np.ma.masked else value for value in index],
            mask=[value is np.ma.masked for value in index],
        )
        cov = np.ma.masked_array(cov)
        return ColorMatrix(index, cov)

    def write(self, fn: str, overwrite: bool = False) -> None:
        """Write the colors to a ECSV formatted file.


        Parameters
        ----------
        fn : str
            File name.

        overwrite : bool, optional
            ``True`` to overwrite existing files.

        """

        colnames = [
            "bands",
            "index",
        ] + [f"cov({blue}-{red})" for blue, red in combinations(Band, 2)]

        rows = []
        for i in range(15):
            blue, red = self.array_index_to_bands(i)
            values = [f"{blue}-{red}", self.index[i], *self.cov[i]]
            rows.append({col: value for col, value in zip(colnames, values)})

        tab = Table(rows)
        tab.write(fn, format="ascii.ecsv", overwrite=overwrite)
