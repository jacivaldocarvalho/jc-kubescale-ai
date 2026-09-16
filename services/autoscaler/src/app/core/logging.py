import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(handler)

    return logger
