from collections import namedtuple
from typing import Any, overload

import astropy.units as u
import numpy as np
from astropy.table import Table
from astropy.time import Time

from .band import Band


class Result:
    """Tabular data in a convenient attribute-based wrapper.


    Parameters
    ----------
    table : `~astropy.table.Table`
        Column names will be used as the ``Result`` attributes.

    """

    def __init__(self, table: Table) -> None:
        self._columns = table.colnames

        for col in table.columns:
            if col == "midpointMjdTai" or col == "expMidptMJD":
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

            setattr(self, col, data)

    def _asdict(self) -> dict:
        return {col: self[col] for col in self.columns}

    @overload
    def __getitem__(self, key: int) -> Any:
        pass

    @overload
    def __getitem__(self, key: slice | list | np.ndarray) -> "Result":
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
            values = [self[col][key] for col in self.columns]

            if isinstance(key, int):
                return namedtuple("ResultRow", *values)

            return Result(Table(values, names=self.columns))

        return getattr(self, key)

    def __len__(self):
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
        tab = Table(self._asdict())
        if "band" in tab.columns and isinstance(tab["band"][0], Band):
            tab["band"] = [str(b) for b in tab["band"]]
        return tab

    @property
    def columns(self) -> list[str]:
        """The column names."""
        return self._columns

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
