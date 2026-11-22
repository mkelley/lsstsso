from types import SimpleNamespace
from typing import Any, overload

import astropy.units as u
import numpy as np
from astropy.table import Column, Table
from astropy.time import Time

from .band import Band

__all__ = ["Result"]


class Result:
    """Tabular data in a convenient attribute-based wrapper.

    Primarily designed for results from the Rubin Science Platform.


    Parameters
    ----------
    table : `~astropy.table.Table`
        Column names will be used as the ``Result`` attributes.  The following
        columns will be implicitly converted from arrays to new objects, as
        needed:

            * "midpointMjdTai" to `~astropy.time.Time` (TAI scale)
            * "expMidptMJD" to `~astropy.time.Time` (TAI scale)
            * "peri_time" to `~astropy.time.Time` (TT scale)
            * "epoch_mjd" to `~astropy.time.Time` (TT scale)
            * "band" to `~lsstsso.band.Band`

    """

    def __init__(self, table: Table) -> None:
        self._columns = table.colnames

        for col in table.columns:
            if (col == "midpointMjdTai" or col == "expMidptMJD") and not isinstance(
                table[col], Time
            ):
                data = Time(table[col], scale="tai", format="mjd")
            elif col in ("peri_time", "epoch_mjd") and not isinstance(table[col], Time):
                data = Time(table[col], scale="tt", format="mjd")
            elif col == "band" and not isinstance(table[col], Band):
                data = np.array(table[col], dtype=Band)
            elif hasattr(table[col], "unit") and table[col].unit is not None:
                data = table[col].quantity
            elif isinstance(table[col], Column):
                data = table[col].data
            else:
                data = table[col]

            setattr(self, col, data)

    @classmethod
    def from_arrays(cls, **kwargs) -> "Result":
        """Initialize from arrays via key-value pairs.


        Examples
        --------

        >>> from lsstsso.result import Result
        >>>
        >>> result = Result.from_arrays(a=[1, 2], b=[3, 4])
        >>> result.a
        array([1, 2])

        """

        return Result(Table(list(kwargs.values()), names=list(kwargs)))

    @classmethod
    def from_rows(cls, rows: list[dict]) -> "Result":
        """Initialize from a list of dictionaries.


        Parameters
        ----------
        rows : list of dict
            List of data rows as dictionaries.


        Examples
        --------

        >>> from lsstsso.result import Result
        >>>
        >>> result = Result.from_rows([{"a": 1, "b": 2}, {"a": 3, "b": 4}])
        >>> result.a
        array([1, 3])

        """

        return Result(Table(rows))

    def _asdict(self) -> dict:
        return {col: self[col] for col in self.columns}

    @overload
    def __getitem__(self, key: int) -> Any: ...

    @overload
    def __getitem__(self, key: slice | list | np.ndarray) -> "Result": ...

    @overload
    def __getitem__(self, key: str) -> u.Quantity | np.ndarray: ...

    def __getitem__(self, key):
        """Get a column or a new result from a row or rows.


        Parameters
        ----------
        key : int, slice, array, or str
            * For integers: returns a single row of data as a new ``ResultRow``.
            * For slices: returns a new ``Result`` based on the slice.
            * For lists or arrays: returns a new ``Result`` based on the
                array indexes or boolean selection.
            * For strings: returns the requested column.


        Returns
        -------
        data : Result, ResultRow, u.Quantity, np.ndarray

        """

        if isinstance(key, int):
            return SimpleNamespace(
                **{col: data[key] for col, data in self._asdict().items()}
            )

        if isinstance(key, int | slice | list | np.ndarray):
            return Result.from_arrays(
                **{name: getattr(self, name)[key] for name in self.columns}
            )

        return getattr(self, key)

    def __len__(self):
        if len(self.columns) == 0:
            return 0

        n = [len(self[col]) for col in self.columns]
        lengths = set(n)
        if len(lengths) != 1:
            raise ValueError("Mismatched column lengths!")

        return next(iter(lengths))

    def __repr__(self):
        return "<Result: " + ",".join(self.columns) + ">"

    def __str__(self):
        return "\n".join(self.as_table().pformat())

    def as_table(self):
        return Table(self._asdict())

    @property
    def columns(self) -> list[str]:
        """The column names."""
        return self._columns

    def rows(self):
        for i in range(len(self)):
            yield self[i]

    def sort(self, field: str, reversed: bool = False):
        """In-place sort by the requested column ."""

        i = np.argsort(self[field])

        if reversed:
            i = i[::-1]

        for f in self._columns:
            self[f][:] = self[f][i]
