import ctypes
import logging
import sys
import time

from ads_reader import ads_reader, SpidevConfig, Ads1256Config

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

    spi_cfg = SpidevConfig(
        spi_speed_hz=1000000,
        spi_mode=1,
        spi_bus=0,
        spi_bits=8,
        chip_select=0,
    )

    logging.info("Opening SPI device...")
    spi = ads_reader.spidev_open(ctypes.byref(spi_cfg))
    if not spi:
        logging.error("Failed to open SPI device")
        return
    logging.info("SPI device opened successfully")
    
    try:
        ads_cfg = Ads1256Config(
            spidev=ctypes.cast(spi, ctypes.c_void_p),
            drate=0xB0,
            gain=0x00,
            drdy_gpio=24,
            pdwn_gpio=17,
        )

        logging.info("Initializing ADS1256...")
        ads = ads_reader.ads1256_open(ctypes.byref(ads_cfg))
        if not ads:
            logging.error("Failed to initialize ADS1256 chip")
            return

        logging.info("ADS1256 successfully initialized")
        time.sleep(1)

        ads_reader.ads1256_close(ads)

    finally:
        logging.info("Closing SPI bus...")
        ads_reader.spidev_close(spi)

    logging.info("ADS Reader exiting...")

if __name__ == "__main__":
    main()
