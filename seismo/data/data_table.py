import typing


class DataTable:
    """Lightweight container which represents a table of data.
    """

    def __init__(self) -> None:
        self.column_names: list[str] = []
        self.column_types: list[type] = []
        self._rows: list[list[typing.Any]] = []
        self._name_to_idx: dict[str, int] = {}

    def get_copy_with_columns(self) -> "DataTable":
        new_table = DataTable()
        for name, typ in zip(
            self.column_names,
            self.column_types,
            strict=True,
        ):
            new_table.add_column(name, typ)
        return new_table

    def add_column(self, column_name: str, column_type: type) -> "DataTable":
        if column_name in self._name_to_idx:
            raise ValueError(f"Column name '{column_name}' already exists.")

        self.column_names.append(column_name)
        self.column_types.append(column_type)
        self._name_to_idx[column_name] = len(self.column_names) - 1

        return self

    def add_columns(self, columns: list[tuple[str, type]]) -> None:
        for column_name, column_type in columns:
            self.add_column(column_name, column_type)

    def add_row(self, row: dict[str, typing.Any]) -> None:
        ordered_row = [row.get(name) for name in self.column_names]
        self.add_row_values(ordered_row)

    def add_row_values(self, row: list[typing.Any]) -> None:
        if len(row) != len(self.column_names):
            raise ValueError(
                "Row length %d does not match number of columns %d." % (
                    len(row),
                    len(self.column_names),
                )
            )
        self._rows.append(row)

    def get_row(self, index: int) -> dict[str, typing.Any]:
        row_values = self._rows[index]
        return {name: val for name, val in zip(
            self.column_names, row_values, strict=False
        )}

    def clear(self) -> None:
        self._rows.clear()

    def __len__(self) -> int:
        return len(self._rows)
