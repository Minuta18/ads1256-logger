import csv
import abc

from . import data_table

class BaseSaver(abc.ABC):
    @abc.abstractmethod
    def save(self, path: str, table: data_table.DataTable):
        pass

class CSVSaver(BaseSaver):
    def save(self, path: str, table: data_table.DataTable):
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(table.column_names)
            writer.writerows(table._rows)
