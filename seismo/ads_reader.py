"""Contains only class ADSReader.

ADSReader - class to manage and read data from ADS1256, using pipyadc.
"""

import types
import typing

import pipyadc

from seismo import config, logging_utils


class ADSReader:
    """Class to manage the ADS1256 reader using pipyadc."""

    def __init__(self, config_: config.Config) -> None:
        """Initialize ADSReader. Requires config as an argument."""
        self.config = config_
        self.adapter_config = config.LibConfigAdapter(self.config.ads)
        self._ch_seq = self.adapter_config.ch_sequence
        self.ads = None

        self.logger = logging_utils.get_logger("SeismoLogger.ADSReader")

        # pipyadc expects a module-like object for configuration, so we create
        # one dynamically from the adapter config.
        self.lib_config = types.ModuleType("ads_config_runtime")
        for key, value in self.adapter_config.__dict__.items():
            setattr(self.lib_config, key, value)

    def __enter__(self) -> typing.Self:
        """ADSReader can be used as a context-manager.

        Class will connect to ADS1256 device automatically.
        """
        self.logger.info("Initializing ADS1256")
        try:
            self.ads = pipyadc.ADS1256(self.lib_config)
            self.ads.cal_self()
            self.logger.info("ADS1256 initialized successfully.")
        except Exception as e:
            self.logger.exception("Failed to initialize ADS1256: {}" % e)
            raise

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Close connection to the ADS1256 device."""
        if self.ads is not None:
            self.ads.stop_close_all()

    def read_channels(self) -> list[int]:
        """Read the active channels as raw 24-bit values."""
        if self.ads is None:
            raise ValueError("ADS reader is not initialized.")

        return self.ads.read_continue(self.lib_config.ch_sequence)

    def read_channels_volts(self) -> list[float]:
        """Read the active channels as voltage values."""
        if self.ads is None:
            raise ValueError("ADS reader is not initialized.")

        raw_data = self.read_channels()
        return [val * self.ads.v_per_digit for val in raw_data]
