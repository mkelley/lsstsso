from collections import namedtuple

import numpy as np
from astropy.table import Table
from astropy.time import Time

from .band import Band


def make_result(table: Table):
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

    ResultRow = namedtuple("ResultBase", table.colnames)
    ResultRow.__doc__ = """A single row of data."""

    class Result(namedtuple("ResultBase", table.colnames)):
        """A table of data."""

        __slots__ = ()

        def __getitem__(self, key: int | slice | str):
            """Get a column or a new result from a row or rows.


            Parameters
            ----------
            key : int, slice, or str
                * For integers: returns a single row of data as a new ``ResultRow``.
                * For slices: returns a new ``Result`` based on the slice.
                * For strings: returns the requested column.

            """

            if isinstance(key, int | slice):
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

            return list(lengths)[0]

        def __repr__(self):
            print(str(self))

        def __str__(self):
            return self.as_table().pprint_all()

        def as_table(self):
            return Table(self._asdict())

        def sort(self, field: str):
            """Sort by the requested column ."""

            i = np.argsort(self[field])
            return Result(*(self[field][i] for field in self._fields))

    columns = []
    for col in table.columns:
        if "Mjd" in col and "Tai" in col:
            columns.append(Time(table[col], scale="tai", format="mjd"))
        elif col in ("peri_time", "epoch_mjd"):
            columns.append(Time(table[col], scale="tt", format="mjd"))
        elif col == "band":
            columns.append(np.array([Band[b] for b in table[col]]))
        elif table[col].unit is None:
            columns.append(table[col].data)
        else:
            columns.append(table[col].quantity)

    return Result(*columns)
