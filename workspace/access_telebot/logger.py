import os
import logging
from logging.handlers import TimedRotatingFileHandler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _add_global_handler(logger):
    # Установка обработчика для общего файла лога
    global_log_file_handler = TimedRotatingFileHandler(
        os.path.join(BASE_DIR, "logs/all.log"), when="midnight"
    )
    global_log_file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        f"%(asctime)s [%(levelname)s] %(message)s"
    )
    global_log_file_handler.setFormatter(formatter)
    logger.addHandler(global_log_file_handler)


def _setup_file_handler(logger, mod_name, prefix=""):
    _add_global_handler(logger)
    # Установка обработчика для специфического файла лога модуля
    module_log_file_handler = TimedRotatingFileHandler(
        os.path.join(BASE_DIR, f"logs/{mod_name}.log"), when="midnight"
    )
    module_log_file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        f"%(asctime)s [%(levelname)s] {prefix} %(message)s"
    )
    module_log_file_handler.setFormatter(formatter)
    logger.addHandler(module_log_file_handler)


def get_logger(mod_name, prefix=""):
    logger = logging.getLogger(mod_name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        _setup_file_handler(logger, mod_name, prefix)

    return logger

