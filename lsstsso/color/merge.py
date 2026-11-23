import numpy as np

from .color_matrix import ColorMatrix


def merge(color_matrices: list[ColorMatrix]) -> ColorMatrix:
    """Merge a set of color matrices into one.


    Parameters
    ----------
    color_matrices: list of ColorMatrix
        The colors to merge.  There must not be any shared colors between them.


    Results
    -------
    merged : ColorMatrix
        The merged colors.


    Raises
    ------
    ValueError
        It is an error if the color matrices are not disjoint.

    """

    # check for shared colors
    index_count = np.sum([~cm.index.mask for cm in color_matrices], 0)
    cov_count = np.sum([~cm.cov.mask for cm in color_matrices], 0)
    if np.any(index_count > 1) or np.any(cov_count > 1):
        raise ValueError("Matrices must be disjoint.")

    result = ColorMatrix()

    for cm in color_matrices:
        result.index[~cm.index.mask] = cm.index[~cm.index.mask]
        result.cov[~cm.cov.mask] = cm.cov[~cm.cov.mask]

    return result
