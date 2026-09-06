from collections import namedtuple
from typing import TypeVar, overload

import astropy.units as u
import numpy as np
from astropy.table import Table
from astropy.time import Time

from .band import Band

ResultClass = TypeVar("Result")
ResultRowClass = TypeVar("ResultRow")


def make_result(table: Table) -> ResultClass:
    """Convert a table into a convenient ``Result`` object.


    Parameters
    ----------
    table : `~astropy.table.Table`
        Column names will be used as the ``Result`` attributes.


    Returns
    -------
    result : Result
        A ``NamedTuple`` with some bells and whistles.

    """

    ResultRow = namedtuple("ResultRow", table.colnames)
    ResultRow.__doc__ = """A single row of data."""

    class Result(namedtuple("Result", table.colnames)):
        """A table of data."""

        __slots__ = ()

        @overload
        def __getitem__(self, key: int) -> ResultRowClass:
            pass

        @overload
        def __getitem__(self, key: slice | list | np.ndarray) -> ResultClass:
            pass

        @overload
        def __getitem__(self, key: str) -> u.Quantity | np.ndarray:
            pass

        def __getitem__(self, key):
            """Get a column or a new result from a row or rows.


            Parameters
            ----------
            key : int, slice, or str
                * For integers: returns a single row of data as a new ``ResultRow``.
                * For slices: returns a new ``Result`` based on the slice.
                * For lists or arrays: returns a new ``Result`` based on the
                  array indexes or boolean selection.
                * For strings: returns the requested column.


            Returns
            -------
            data : Result, ResultRow, u.Quantity, np.ndarray

            """

            if isinstance(key, int | slice | list | np.ndarray):
                values = [self[field][key] for field in self._fields]

                if isinstance(key, int):
                    return ResultRow(*values)

                return Result(*values)

            return getattr(self, key)

        def __len__(self):
            n = [len(self[field]) for field in self._fields]
            lengths = set(n)
            if len(lengths) != 1:
                raise ValueError("Mismatched column lengths!")

            return next(iter(lengths))

        def __str__(self):
            return "\n".join(self.as_table().pformat_all())

        def as_table(self):
            tab = Table(self._asdict())
            if "band" in tab.columns() and isinstance(tab["band"][0], Band):
                tab["band"] = [str(b) for b in tab["band"]]
            return tab

        def columns(self) -> list[str]:
            """The column names."""
            return self._fields

        def rows(self):
            for i in range(len(self)):
                yield self[i]
            raise StopIteration  # noqa: PLR1708

        def sort(self, field: str, reversed: bool = True):
            """In-place sort by the requested column ."""

            i = np.argsort(self[field])

            if reversed:
                i = i[::-1]

            for f in self._fields:
                self[f][:] = self[f][i]

    columns = []
    for col in table.columns:
        if "Mjd" in col and "Tai" in col:
            data = Time(table[col], scale="tai", format="mjd")
        elif col in ("peri_time", "epoch_mjd"):
            data = Time(table[col], scale="tt", format="mjd")
        elif col == "band":
            data = np.array([Band[b] for b in table[col]])
        elif table[col].unit is None:
            data = table[col].data
        else:
            data = table[col].quantity

        if hasattr(data, "mask") and not any(data.mask):
            if hasattr(data, "unmasked"):
                data = data.unmasked
            else:
                data = data.data

        columns.append(data)

    return Result(*columns)
