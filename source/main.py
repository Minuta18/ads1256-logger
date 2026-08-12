import ctypes
import os
import logging
import sys

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

lib_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../cmake-build-debug/ads_reader/libads_reader.so")
)

if not os.path.exists(lib_path):
    raise FileNotFoundError(f"Shared library not found at {lib_path}")

ads_reader = ctypes.CDLL(lib_path)
ads_reader.get_string.restype = ctypes.c_char_p

def main() -> None:
    logging.info("ADS Reader starting...")

    c_string = ads_reader.get_string()
    logging.info(f"Received string: {c_string}")

    logging.info("ADS Reader exiting...")

if __name__ == "__main__":
    main()
