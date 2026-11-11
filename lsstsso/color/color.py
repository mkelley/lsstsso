from dataclasses import dataclass

import astropy.units as u
import numpy as np

from ..band import Band


@dataclass
class Color:
    """A color measurement.


    Parameters
    ----------
    left, right : Band
        The bandpasses for the measurement.

    index, unc : u.Quantity
        The color measurement and uncertainty in units of mag.  May be arrays.


    Examples
    --------
    >>> from lsstsso import Band
    >>> from lsstsso.color import Color
    >>>
    >>> print(Color(Band.u, Band.g, 1.1, 0.02))
    u-g = 1.100 ± 0.020 mag

    Strings may also be used

    """

    left: Band
    right: Band
    index: u.Quantity
    unc: u.Quantity

    def __post_init__(self) -> None:
        # normalize inputs
        self.left = Band(self.left)
        self.right = Band(self.right)
        self.index = u.Quantity(self.index, u.mag)
        self.unc = u.Quantity(self.unc, u.mag)

    def __repr__(self) -> str:
        if np.size(self.index) > 1:
            s = str(self.mean())
            n = len(self.index)
            return f"<Color {s} (mean of {n} points)>"

        return f"<Color {self.left}-{self.right} = {self.index.value:0.3f} ± {self.unc.value:0.3f} mag>"

    def __str__(self) -> str:
        return repr(self)[7:-1]

    def mean(self) -> "Color":
        """Weighted average.


        Returns
        -------
        mean : Color

        """

        m, sw = np.average(self.index, weights=self.unc**-2, returned=True)
        return Color(self.left, self.right, m, sw ** -(1 / 2))
