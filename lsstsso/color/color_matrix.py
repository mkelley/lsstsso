# def print_color_matrix(color_matrix: np.ma.MaskedArray, **kwargs):
#     with np.printoptions(formatter={"float": "{:+0.3f}".format}):
#         s = str(color_matrix.filled(np.nan))

#     s = s.replace("nan", " --- ").replace("+", " ")
#     print(s, **kwargs)

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

import astropy.units as u
import numpy as np

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
        self.value = np.ma.zeros((6, 6))
        self.unc = np.zeros_like(self.value)

        weights = np.zeros_like(self.value)
        for color in colors:
            i = list(Band).index(color.blue)
            j = list(Band).index(color.red)

            weights[i, j] = color.unc**-2
            self.value[i, j] += color.index * weights[i, j]

        # average, as appropriate, and fill in the lower triangle
        for i, j in combinations(range(6), 2):
            if weights[i, j] == 0:
                continue

            self.value[i, j] /= color.unc
            self.unc[i, j] = 1 / np.sqrt(weights[i, j])

            self.value[j, i] = -self.value[i, j]
            self.unc[j, i] = self.unc[j, i]

        # mask empty colors
        self.value[self.value == 0] = np.ma.masked
        self.unc[self.value == 0] = np.ma.masked

    def __repr__(self):
        n = np.sum(~np.triu(self.value).mask)
        return f"<ColorMatrix {n} values>"

    def __str__(self):
        for i, j in combinations(range(6), 2):
            print(Color(list(Band)[i], list(Band)[j], self.value[i, j], self.unc[i, j]))

    def fill(self):
        """Fill in missing transformations that can be calculated."""

        # recursively fill them in
        while True:
            new_colors = []
            for i, j in combinations(range(6), 2):
                # already measured?
                if self.value[i, j] is not np.ma.masked:
                    continue

                # OK blue-red is missing, now find what we can calculate it from, single
                # steps only
                colors = []
                var = []
                for band in set(range(6)) - set([i, j]):
                    if not self.value.mask[i, band] and not self.value.mask[band, j]:
                        colors.append(self.value[i, band] + self.value[band, j])
                        var.append(self.unc[i, band] ** 2 + self.unc[band, j] ** 2)

                if len(colors) == 0:
                    continue

                # average them together
                c, sw = np.average(colors, weights=np.array(var) ** -1, returned=True)
                cu = sw**-0.5
                new_colors[(i, j)] = c, cu
                new_colors[(j, i)] = -c, cu

            if len(new_colors) == 0:
                break

            # save updating for last to avoid propagating newly calculated colors in
            # the current iteration
            for (i, j), (value, unc) in new_colors.items():
                self.value[i, j] = value
                self.unc[i, j] = unc
