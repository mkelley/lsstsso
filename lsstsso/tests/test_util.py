import numpy as np

from ..util import merge_sets, weighted_mean


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


def test_merge_sets():
    # first, nothing overlaps
    sets = [{1, 2}, {3, 4}, {5, 6}]
    result = merge_sets(sets)
    assert result == sets

    sets.append({4, 5})
    result = merge_sets(sets)
    assert len(result) == 2
    assert {1, 2} in result
    assert {3, 4, 5, 6} in result

    sets.append({2, 5})
    result = merge_sets(sets)
    assert len(result) == 1
    assert {1, 2, 3, 4, 5, 6} in result

    sets = [{1, 2}, {2, 3}, {2, 5}, {4, 6}, {5, 7}]
    result = merge_sets(sets)
    assert len(result) == 2
    assert {1, 2, 3, 5, 7} in result
    assert {4, 6} in result
