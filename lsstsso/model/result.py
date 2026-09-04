from astropy.table import Table


class Result:
    def __init__(self, result: Table):
        self.table = result

        for col in result.colnames:
            setattr(self, col, self._get_result_getter(col))

    def __getitem__(self, item: str | int | slice):
        if isinstance(item, str):
            return self.table[item]

        return Result(self.table[item])

    def __repr__(self) -> str:
        return repr(self.table)

    def __str__(self) -> str:
        return str(self.table)

    def _get_result_getter(self, col):
        def getter():
            return self.result[col].quantity

        return getter
