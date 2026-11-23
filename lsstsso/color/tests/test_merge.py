import numpy as np

from ...band import Band
from ..color import Color
from ..color_matrix import ColorMatrix
from ..merge import merge


def test_merge():
    cm1 = ColorMatrix.from_colors(
        [
            Color(Band.u, Band.g, 1.0, 0.2),
            Color(Band.g, Band.r, 1.2, 0.02),
            Color(Band.u, Band.i, 1.4, 0.1),
        ]
    )
    cm2 = ColorMatrix.from_colors(
        [
            Color(Band.z, Band.y, 0.0, 0.01),
        ]
    )

    merged = merge([cm1, cm2])
    assert np.sum(merged.index.mask) == np.sum(cm1.index.mask * cm2.index.mask)
    assert np.sum(merged.cov.mask) == np.sum(cm1.cov.mask * cm2.cov.mask)

    assert np.ma.allclose(merged.index[[0, 2, 5, 14]], cm1.index[[0, 2, 5, 14]])

    i = np.ix_([0, 2, 5], [0, 2, 5])
    assert np.ma.allclose(merged.cov[i], cm1.cov[i])
    assert np.ma.allclose(merged.cov[[14]], cm1.cov[[14]])
