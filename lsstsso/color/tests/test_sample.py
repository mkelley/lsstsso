import numpy as np

from ...band import Band
from ..color import Color
from ..color_matrix import ColorMatrix
from ..sample import sample


def test_sample():
    index = np.ma.zeros(15)
    index.mask = True
    index[0] = 1.0
    index[2] = 1.4
    index[5] = 1.2

    cov = np.ma.zeros((15, 15))
    cov.mask = True
    cov[0, 0] = 0.2**2
    cov[2, 2] = 0.1**2
    cov[5, 5] = 0.02**2
    cov[0, 2] = cov[2, 0] = 0.2 * 0.1
    cov[0, 5] = cov[5, 0] = -0.2 * 0.02
    cov[2, 5] = cov[5, 2] = 0

    cm = ColorMatrix.from_colors(
        [
            Color(Band.u, Band.g, 1.0, 0.2),
            Color(Band.g, Band.r, 1.2, 0.02),
            Color(Band.u, Band.i, 1.4, 0.1),
        ]
    )

    result = sample(cm, [Band.u, Band.g, Band.r])

    assert len(result) == 2

    expected = np.ma.zeros(15)
    expected.mask = True
    expected[0] = 1.0
    expected[5] = 1.2
    assert np.ma.allclose(result.index, expected)

    cov = np.ma.zeros((15, 15))
    cov.mask = True
    cov[0, 0] = 0.2**2
    cov[5, 5] = 0.02**2
    cov[0, 5] = cov[5, 0] = -0.2 * 0.02
    assert np.ma.allclose(result.cov, cov)
