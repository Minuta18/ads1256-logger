import ctypes
import logging
import sys
import time

import ads_reader

log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

level_dict = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("system.log"),
    ],
)


def main() -> None:
    logging.info("ADS Reader starting...")

    spi_bus = ads_reader.SPIBus()
    spi_bus.open()

    ads_device = ads_reader.ADS1256(
        spi_bus,
        drdy_gpio=17,
        pdwn_gpio=27
    )
    ads_device.open()

    for _ in range(20):
        raw_val = ads_device.read_channel(0)
        logging.info(f"Channel 0: {raw_val}")

    ads_device.close()
    spi_bus.close()

    logging.info("ADS Reader exiting...")

if __name__ == "__main__":
    main()
