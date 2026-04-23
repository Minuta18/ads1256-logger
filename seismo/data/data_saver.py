import abc
import csv
import os

from . import data_table


class BaseSaver(abc.ABC):
    @abc.abstractmethod
    def save(
        self,
        path: str,
        table: data_table.DataTable,
    ) -> None:
        pass

class CSVSaver(BaseSaver):
    def save(
        self,
        path: str,
        table: data_table.DataTable,
    ) -> None:
        mode = "w"
        if os.path.exists(path):
            mode = "a"

        with open(path, mode, newline="") as f:
            writer = csv.writer(f)
            if mode == "w":
                writer.writerow(table.column_names)
            writer.writerows(table._rows)
