import os
import logging
from logging.handlers import TimedRotatingFileHandler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_logger(mod_name, prefix=""):
    logger = logging.getLogger(mod_name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # create file handler which logs even debug messages
        fh = TimedRotatingFileHandler(
            os.path.join(BASE_DIR, f"logs/{mod_name}.log"), when="midnight"
        )
        fh.setLevel(logging.INFO)

        # create formatter and add it to the handlers
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter(
            f"%(asctime)s [%(levelname)s] {prefix} %(message)s"
        )
        fh.setFormatter(formatter)

        # add the handlers to the logger
        logger.addHandler(fh)

    return logger
