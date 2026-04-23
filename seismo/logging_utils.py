import logging
import sys

from seismo import config


def setup_logging(cfg: config.Config) -> None:
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    level_dict = {
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
    }

    logging.basicConfig(
        level=level_dict.get(cfg.log_level, logging.INFO),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("system.log"),
        ],
    )

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
