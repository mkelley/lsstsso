"""
Based on ``Bands`` from mskpy, https://doi.org/10.5281/zenodo.17516897, see
licenses/
"""

from enum import Enum
import astropy.units as u


class Band(Enum):
    u = 0
    g = 1
    r = 2
    i = 3
    z = 4
    y = 5

    def __eq__(self, band):
        return self.value == band.value

    def __hash__(self):
        return self.value

    def __lt__(self, band):
        return self.value < band.value

    def __gt__(self, band):
        return self.value > band.value

    def __repr__(self):
        return f"<Band: {self}, {self.wave}>"

    def __str__(self):
        return self.name

    @property
    def wave(self):
        wavelengths = [372.4, 480.7, 622.1, 755.9, 868.0, 975.3] * u.nm
        return wavelengths[self.value]
