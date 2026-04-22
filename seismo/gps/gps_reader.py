import datetime
import subprocess
import threading
import time

import pynmea2
import serial

from seismo import config, logging_utils, status_collector


class GPSReader:
    """Class to manage GPS reading using pynmea2."""

    def __init__(self,
        cfg: config.GPSConfig,
        status_collector: status_collector.StatusCollector|None = None,
    ):
        self.cfg = cfg
        self.status_collector = status_collector

        self.gps_port = cfg.gps_port
        self.gps_baudrate = cfg.gps_baudrate
        self.last_fix = {
            "lat": 0.0, "lon": 0.0, "alt": 0.0, "timestamp": None,
            "num_sats": 0, "status": 0,
        }

        self._logger = logging_utils.get_logger("SeismoLogger.GPSReader")
        self._is_ready = threading.Event()

        self._running = False
        self._lock = threading.Lock()

    def is_ready(self) -> bool:
        return self._is_ready.is_set()

    def _parse_line(self, line: str):
        try:
            # Not a valid NMEA sentence
            if not line.startswith("$"):
                return

            msg = pynmea2.parse(line)
            with self._lock:
                if isinstance(msg, pynmea2.types.talker.GGA):
                    self.last_fix["lat"] = msg.latitude
                    self.last_fix["lon"] = msg.longitude
                    self.last_fix["alt"] = msg.altitude
                    self.last_fix["num_sats"] = int(msg.num_sats)
                    self.last_fix["status"] = int(msg.gps_qual)

                    to_update = {
                        "gps_lat": self.last_fix["lat"],
                        "gps_lon": self.last_fix["lon"],
                        "gps_alt": self.last_fix["alt"],
                        "gps_sats": self.last_fix["num_sats"],
                    }

                    for key, value in to_update.items():
                        if self.status_collector:
                            self.status_collector.update_status(key, value)

                    if self.last_fix["num_sats"] >= 4 and \
                        self.last_fix["status"] > 0:
                        self._is_ready.set()
                elif isinstance(msg, pynmea2.types.talker.RMC):
                    if msg.datestamp and msg.timestamp:
                        self.last_fix["timestamp"] = datetime.datetime.combine(
                            msg.datestamp, msg.timestamp,
                        )

                        self._sync_system_time(self.last_fix["timestamp"])
        except pynmea2.ParseError:
            self._logger.warning(
                "Received malformed NMEA sentence. Might be due to GPS"
                " signal issues.",
            )

    def _sync_system_time(self, gps_time: datetime.datetime):
        system_time = datetime.datetime.now(datetime.UTC)
        time_diff = abs((gps_time - system_time).total_seconds())
        if time_diff < 1:
            self._logger.info(
                "System time is already in sync with GPS time"
                f" (diff: {time_diff:.2f}s).",
            )
            return

        try:
            self._logger.info(
                "Syncing system time to GPS time."
                f" Current diff: {time_diff:.2f}s.",
            )

            gps_time_str = gps_time.strftime("%Y-%m-%d %H:%M:%S")
            subprocess.run(
                ["sudo", "date", "-s", gps_time_str],
                check=True,
            )

            self._logger.info(
                f"System time synced to GPS time: {gps_time_str}",
            )
        except subprocess.CalledProcessError as e:
            self._logger.error(f"Failed to sync system time: {e}")

    def get_last_fix(self) -> dict:
        return self.last_fix.copy()

    def wait_for_gps(self):
        """Waits until a valid GPS fix is obtained or timeout occurs."""
        self._logger.info(
            "Waiting for GPS fix with at least 4 satellites and valid status...",
        )

        start_time = datetime.datetime.now()
        current_retry = 1
        while not self.is_ready():
            fix = self.get_last_fix()
            self._logger.info(f"Connection attempt #{current_retry}. Details:")
            self._logger.info(f"Connected satellites: { fix['num_sats'] }")
            self._logger.info(f"GPS status: { fix['status'] }")

            if (datetime.datetime.now() - start_time).total_seconds() > \
                self.cfg.timeout:
                self._logger.warning(
                    "Unable to obtain GPS fix. Continuing with system time.",
                )
                return

            time.sleep(self.cfg.retry_interval)
            current_retry += 1

        self._logger.info(
            f"GPS fix obtained with { self.last_fix['num_sats'] } satellites.",
        )

    def gps_loop(self):
        """Main loop to read GPS data continuously."""
        try:
            with serial.Serial(self.gps_port, self.gps_baudrate, timeout=1) as ser:
                self._logger.info(
                    f"Started GPS reading loop on {self.gps_port} "
                    f"at baudrate {self.gps_baudrate}.",
                )

                while True:
                    line = ser.readline().decode("ascii", errors="replace").strip()
                    if line:
                        self._parse_line(line)
        except Exception as e:
            self._logger.error(
                f"Error in GPS reading loop: {e}", exc_info=True,
            )
            self._logger.info(
                "Attempting to restart GPS reading loop in 5 seconds...",
            )
            time.sleep(5)
