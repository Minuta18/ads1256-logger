import queue
import dataclasses
import threading

from . import data_saver
from . import data_table
import config

@dataclasses.dataclass
class SaveRequest:
    path: str
    table: data_table.DataTable

class DataQueue:
    '''
    Queue for saving data tables to disk asynchronously, so that the main 
    data collection loop is not blocked by file I/O.
    '''

    def __init__(self, saver: data_saver.BaseSaver, config_: config.Config):
        self._saver = saver
        self._config = config_

        # 20 would be enough to hold 20x the buffer size, which should be more 
        # than enough to handle any backlog without consuming too much memory.
        self._queue = queue.Queue(maxsize=20)

        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._stop_event = threading.Event()

        self._worker_thread.start()

    def put(self, path: str, table: data_table.DataTable):
        if not self._stop_event.is_set():
            self._queue.put(SaveRequest(path=path, table=table))

    def _worker(self):
        while not self._stop_event.is_set() or not self._queue.empty():
            try:
                task = self._queue.get(timeout=0.1)
                self._saver.save(task.path, task.table)
                self._queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                ...

    def join(self):
        self._queue.join()

    def stop(self):
        self._stop_event.set()
        self._worker_thread.join()
