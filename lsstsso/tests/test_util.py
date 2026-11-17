import numpy as np

from ..util import weighted_mean


def test_weighted_mean():
    x = np.array([1, 2])
    xunc = np.array([0.01, 0.01])
    m, munc = weighted_mean(x, xunc)
    assert np.isclose(m, 1.5)
    assert np.isclose(munc, np.sqrt(2) / 2 * 0.01)

    x = np.array([1, 2, np.nan])
    xunc = np.array([0.01, 0.01, 1])
    m, munc = weighted_mean(x, xunc)
    assert np.isclose(m, 1.5)
    assert np.isclose(munc, np.sqrt(2) / 2 * 0.01)

    x = np.array([np.nan, np.nan, np.nan])
    xunc = np.array([0.01, 0.01, 1])
    m, munc = weighted_mean(x, xunc)
    assert np.isnan(m)
    assert np.isnan(munc)

    x = np.array([1, 2])
    xunc = np.array([0.01, 0.02])
    m, munc = weighted_mean(x, xunc)
    assert np.isclose(m, 1.2)
    assert np.isclose(munc, 0.00894427190999916)
