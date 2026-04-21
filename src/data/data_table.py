import typing

class DataTable:
    '''
    Lightweight container which represents a table of data.
    '''

    def __init__(self):
        self.column_names: typing.List[str] = []
        self.column_types: typing.List[typing.Type] = []
        self._rows: typing.List[typing.List[typing.Any]] = []
        self._name_to_idx: typing.Dict[str, int] = {}

    def add_column(self, column_name: str, column_type: typing.Type) -> 'DataTable':
        if column_name in self._name_to_idx:
            raise ValueError(f"Column name '{column_name}' already exists.")
        
        self.column_names.append(column_name)
        self.column_types.append(column_type)
        self._name_to_idx[column_name] = len(self.column_names) - 1

        return self

    def add_columns(self, columns: typing.List[typing.Tuple[str, typing.Type]]):
        for column_name, column_type in columns:
            self.add_column(column_name, column_type)

    def add_row(self, row: typing.Dict[str, typing.Any]):
        ordered_row = [row.get(name) for name in self.column_names]
        self.add_row_values(ordered_row)

    def add_row_values(self, row: typing.List[typing.Any]):
        if len(row) != len(self.column_names):
            raise ValueError(
                f"Row length {len(row)} does not match number of columns {len(self.column_names)}."
            )
        self._rows.append(row)

    def get_row(self, index: int) -> typing.Dict[str, typing.Any]:
        row_values = self._rows[index]
        return {name: val for name, val in zip(self.column_names, row_values)}
    
    def clear(self):
        self._rows.clear()

    def __len__(self):
        return len(self._rows)
    