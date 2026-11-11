"""

The color transformation matrix:

      u   g   r   i   z   y
u |   0 u-g u-r u-i u-z u-y |
g | g-u   0 g-r g-i g-z g-y |
r | r-u r-g   0 r-i r-z r-y |
i | i-u i-g i-r   0 i-z i-y |
z | z-u z-g z-r z-i   0 z-y |
y | y-u y-g y-r y-i y-z   0 |

For example, want r-i have, g-i and g-r

Get the sub-matrix, S:

      g   i
g |   1 g-i |
r | r-g r-i |

--> r-i = g-i + r-g

want r-y, have g-r, g-y:

      g   y
g |   1 g-y |
r | r-g r-y |

r-y = g-y + r-g

and for y-r:

      g   r
g |   1 g-r |
y | y-g y-r |

y-r = g-r + y-g

"""

from itertools import combinations, product

import numpy as np
from astropy.io import ascii
from astropy.table import Table
from numpy.ma.core import MaskedConstant
from scipy.optimize import curve_fit

from ..band import Band
from .color import Color


class ColorMatrix:
    """Color transformation matrix.

    Use this class to convert between colors.


    Parameters
    ----------
    colors : array of Color, optional
        The measured colors.  If a color contains arrays, they will be averaged.
        If a color is given twice, they will be averaged.


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
    >>> cm = ColorMatrix(colors)
    >>> print(cm)
    >>> cm.transform(0 * u.mag, 0.03 * u.mag, Band.u, Band.g)

    """

    def __init__(self, colors: list[Color] | None = None):
        self.index = np.ma.zeros((6, 6))
        self.unc = np.ma.zeros_like(self.index)

        weights = np.zeros_like(self.index)
        count = np.zeros(self.index.shape, int)
        for color in colors if colors else []:
            if np.size(color.index) > 1:
                color = color.mean()

            i = list(Band).index(color.left)
            j = list(Band).index(color.right)

            weight = color.unc.value**-2
            if i < j:
                self.index[i, j] += color.index.value * weight
                weights[i, j] += weight
            else:
                self.index[j, i] += -color.index.value * weight
                weights[j, i] += weight

            count[i, j] += 1
            count[j, i] += 1

        # average, as appropriate, and fill in the lower triangle
        for i, j in combinations(range(6), 2):
            if count[i, j] == 0:
                continue

            self.index[i, j] /= weights[i, j]
            self.unc[i, j] = 1 / np.sqrt(weights[i, j])

            self.index[j, i] = -self.index[i, j]
            self.unc[j, i] = self.unc[i, j]

        # mask empty colors
        self.index.mask = count == 0
        self.unc.mask = self.index.mask

    def __repr__(self):
        n = np.sum(~np.triu(self.index.mask))
        return f"<ColorMatrix: {n} values>"

    def __str__(self):
        lines = []
        for i, j in combinations(range(6), 2):
            if self.index[i, j] is np.ma.masked:
                continue
            color = Color(
                list(Band)[i], list(Band)[j], self.index[i, j], self.unc[i, j]
            )
            lines.append(str(color))
        return "\n".join(lines)

    def __getitem__(
        self, bands: tuple[Band | str, Band | str]
    ) -> Color | MaskedConstant:
        """a - b color."""
        a, b = [Band(x) for x in bands]
        i = list(Band).index(a)
        j = list(Band).index(b)

        if self.index[i, j] is np.ma.masked:
            return np.ma.masked

        return Color(a, b, self.index[i, j], self.unc[i, j])

    def solve(self) -> "ColorMatrix":
        """New color solution with least-squares approach."""

        def to_index(i, j):
            return int(11 / 2 * i - i**2 / 2 - 1) + j - i

        def from_index(k):
            """
            [  0    1    2    3    4    5    6    7    8    9   10   11   12   13   14]
            [u-g, u-r, u-i, u-z, u-y, g-r, g-i, g-z, g-y, r-i, r-z, r-y, i-z, i-y, z-y]
            """

            return [
                (0, 1),
                (0, 2),
                (0, 3),
                (0, 4),
                (1, 2),
                (1, 3),
                (1, 4),
                (1, 5),
                (2, 3),
                (2, 4),
                (2, 5),
                (3, 4),
                (3, 5),
                (4, 5),
            ][k]

        # there may be up to 75 equations
        A = np.zeros((75, 15))
        b = np.zeros((75,))
        unc = np.ones((75,))

        bands = list(Band)

        # track the equation we are on
        eqn = 0

        # the first equations are trivial
        print("Equations:")
        for vars, j in combinations(range(6), 2):
            if self.index[vars, j] is not np.ma.masked:
                A[eqn, to_index(vars, j)] = 1
                b[eqn] = self.index[vars, j]
                unc[eqn] = self.unc[vars, j]
                eqn += 1
                print(f"  {bands[vars]}-{bands[j]} = {self.index[vars, j]}")

        # the next equations are two color combinations
        for i, j, k in combinations(range(6), 3):
            n = (
                int(self.index[i, j] is not np.ma.masked)
                + int(self.index[i, k] is not np.ma.masked)
                + int(self.index[j, k] is not np.ma.masked)
            )
            if n < 2:
                continue

            if self.index[i, j] is not np.ma.masked:
                A[eqn, [to_index(i, k), to_index(j, k)]] = [1, -1]
                b[eqn] = self.index[i, j]
                unc[eqn] = self.unc[i, j]
                eqn += 1
                print(
                    f"  {bands[i]}-{bands[k]} - ({bands[j]}-{bands[k]}) = {bands[i]}-{bands[j]}"
                )

            if self.index[i, k] is not np.ma.masked:
                A[eqn, [to_index(i, j), to_index(j, k)]] = [1, 1]
                b[eqn] = self.index[i, k]
                unc[eqn] = self.unc[i, k]
                eqn += 1
                print(
                    f"  {bands[i]}-{bands[j]} + {bands[j]}-{bands[k]} = {bands[i]}-{bands[k]}"
                )

            if self.index[j, k] is not np.ma.masked:
                A[eqn, [to_index(i, j), to_index(i, k)]] = [-1, 1]
                b[eqn] = self.index[j, k]
                unc[eqn] = self.unc[j, k]
                print(
                    f"  -({bands[i]}-{bands[j]}) + {bands[i]}-{bands[k]} = {bands[j]}-{bands[k]}"
                )

        # least squares fit

        def model(A, *x):
            return A @ np.array(x)

        guess = np.array(
            [
                1.83,
                2.42,
                2.63,
                2.68,
                2.71,
                0.59,
                0.8,
                0.85,
                0.88,
                0.21,
                0.26,
                0.29,
                0.05,
                0.08,
                0.03,
            ]
        )

        # remove unused equations
        A = A[:eqn]
        b = b[:eqn]
        unc = unc[:eqn]

        # remove unused variables
        vars = np.flatnonzero(np.sum(A**2, 0))
        A = A[:, vars]
        guess = guess[vars]

        fit, cov = curve_fit(
            model,
            A,
            b,
            p0=guess,
            sigma=unc,
            absolute_sigma=True,
            method="trf",
        )
        fit_unc = np.sqrt(np.diag(cov))

        print("\nSolution:")
        colors = []
        for k, index in enumerate(vars):
            vars, j = from_index[index]
            colors.append(Color(bands[vars], bands[j], fit[k], fit_unc[k]))
            print(f"  {colors[-1]}")

        return ColorMatrix(colors)

    @staticmethod
    def read(fn: str) -> "ColorMatrix":
        """Read color matrix object from a file.

        The file is an astropy Table written in ecsv format via ``.write()``.


        Parameters
        ----------
        fn : string
            The file name from which to read.

        Returns
        -------
        cm : ColorMatrix

        """

        tab = ascii.read(fn, format="ecsv")

        cm = ColorMatrix()
        for i, j in product(range(6), range(6)):
            row = i
            col = list(Band)[j].value
            index, unc, mask = tab[col][row]
            cm.index[i, j] = index
            cm.index.mask[i, j] = mask
            cm.unc[i, j] = unc
            cm.unc.mask[i, j] = mask

        return cm

    def write(self, fn: str, overwrite: bool = False) -> None:
        """Read color matrix object from a file.

        The file will be an astropy Table written in ecsv format.


        Parameters
        ----------
        fn : string
            The file name to which to write.

        overwrite : bool, optional
            Set to ``True`` to overwrite an existing file.

        """

        def cell(i, j):
            return (self.index[i, j], self.unc[i, j], self.index.mask[i, j])

        rows = []
        bands = [b.value for b in list(Band)]
        for i in range(6):
            row = {"band": bands[i]}
            row |= {bands[j]: cell(i, j) for j in range(6)}
            rows.append(row)

        tab = Table(rows)
        tab.write(fn, overwrite=overwrite)
