import time 
import threading
import psutil

import shared_modules.logging_utils as logging_utils
from shared_modules import config

class StatusCollector:
    def __init__(self, cfg: config.Config):
        self._logger = logging_utils.get_logger("SeismoLogger.StatusCollector")

        self._initial_time = time.time()
        self._update_interval = cfg.web_server.data_update_interval

        self._data = {
            "uptime": 0.0,
            "cpu_usage": 0,
            "memory_usage": 0,
            "disk_usage": 0,
            "is_running": True,
            "last_update": time.time(),

            "gps_lat": 0.0,
            "gps_lon": 0.0,
            "gps_alt": 0.0,
            "gps_sats": 0.0,

            "queue_load": 0.0,
            
            "total_batches_saved": 0,
            "last_batch_time": "Never",            
        }

        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = None

    def start(self):
        self._thread = threading.Thread(
            target=self._run, daemon=True, name="StatusCollectorThread"
        )
        self._thread.start()
        self._logger.info("Worker started.")

    def update_status(self, key, value):
        with self._lock:
            if key in self._data:
                self._data[key] = value

    def update_common_values(self):
        with self._lock:
            self._data["uptime"] = time.time() - self._initial_time
            self._data["is_running"] = True
            self._data["cpu_usage"] = psutil.cpu_percent()
            self._data["memory_usage"] = psutil.virtual_memory().percent
            self._data["disk_usage"] = psutil.disk_usage('/').percent
            self._data["last_update"] = time.time()

    def _run(self):
        while not self._stop_event.is_set():
            try:
                self.update_common_values()
            except Exception as e:
                self._logger.error(f"Error occurred while updating status: {e}")
            time.sleep(self._update_interval)
    
    def get_all(self):
        with self._lock:
            return self._data.copy()
        
    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        self._logger.info("Worker stopped.")
    