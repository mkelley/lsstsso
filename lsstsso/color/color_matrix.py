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

from itertools import combinations

import numpy as np
from numpy.ma.core import MaskedConstant

from .color import Color
from ..band import Band


class ColorMatrix:
    """Color transformation matrix.

    Use this class to convert between colors.


    Parameters
    ----------
    colors : array of Color
        The measured colors.  If a color contains arrays, they will be averaged.
        If a color is given twice, they will be averaged.

    fill : bool, optional
        If ``True``, transformations between colors not measured will be
        calculated from multi-step transformations, e.g., compute u-r from u-g
        and g-r.


    Notes
    -----
    Currently, the fewest number of steps takes precedence, e.g., a measured u-r
    will be used over u-g + g-r, even if the latter has a lower uncertainty.

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
    >>> cm.transform(0 * u.mag, 0.03 * u.mag, Band.u, Band.i)

    """

    def __init__(self, colors: list[Color], fill: bool = True):
        self.index = np.ma.zeros((6, 6))
        self.unc = np.zeros_like(self.index)

        weights = np.zeros_like(self.index)
        count = np.zeros(self.index.shape, int)
        for color in colors:
            i = list(Band).index(color.left)
            j = list(Band).index(color.right)

            weights[i, j] = color.unc.value**-2
            self.index[i, j] += color.index.value * weights[i, j]
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

        if fill:
            self.fill()

    def __repr__(self):
        n = np.sum(~np.triu(self.index).mask)
        return f"<ColorMatrix {n} values>"

    def __str__(self):
        for i, j in combinations(range(6), 2):
            print(Color(list(Band)[i], list(Band)[j], self.index[i, j], self.unc[i, j]))

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

    def fill(self):
        """Fill in missing transformations that can be calculated."""

        # recursively fill them in
        while True:
            new_colors = []
            for i, j in combinations(range(6), 2):
                # already measured?
                if self.index[i, j] is not np.ma.masked:
                    continue

                # OK blue-red is missing, now find what we can calculate it from, single
                # steps only
                colors = []
                unc = []
                for band in set(range(6)) - set((i, j)):
                    if not self.index.mask[i, band] and not self.index.mask[band, j]:
                        colors.append(self.index[i, band] + self.index[band, j])
                        unc.append(np.hypot(self.unc[i, band], self.unc[band, j]))

                if len(colors) == 0:
                    continue

                # chose the lowest uncertainty
                k = np.argmin(unc)
                new_colors.append((i, j, colors[k], unc[k]))

            if len(new_colors) == 0:
                break

            # save updating for last to avoid propagating newly calculated colors in
            # the current iteration
            for i, j, value, unc in new_colors:
                self.index[i, j] = value
                self.unc[i, j] = unc

                self.index[j, i] = -value
                self.unc[j, i] = unc
