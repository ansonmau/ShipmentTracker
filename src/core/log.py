import logging
from datetime import datetime
import os
from src.core.utils import create_file

class MyLogger:
    _time           = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    _log_file_path  = os.path.join("./logs", "{}.log".format(_time))
    _level          = logging.INFO
    _loggers        = []
    _console_out    = False
    _default_format = "%(levelname)s/%(name)s: %(message)s"

    def __init__(self, name):
        self._name = name
        self._logger = logging.getLogger(name)
        self._logger.setLevel(MyLogger._level)
        MyLogger._loggers.append(self)

    # ────────────────────────────────< API >──────────────────────────────
    def info(self, msg):
        self._logger.info(msg)

    def warning(self ,msg):
        self._logger.warning(msg)

    def critical(self ,msg):
        self._logger.critical(msg)

    def debug(self ,msg):
        self._logger.debug(msg)

    def error(self ,msg):
        self._logger.error(msg)

    def set_level(self, level):
        self._logger.setLevel(level)

    # ───────────────────────────< static methods >───────────────────────────
    @staticmethod
    def set_global_level(level_name):
        levels = {
                "debug": logging.DEBUG,
                "info":  logging.INFO,
                }
        choice = levels[level_name]

        MyLogger._level = choice
        for logger in MyLogger._loggers:
            logger.set_level(choice)

    @staticmethod
    def init_file_handler():
        create_file(MyLogger._log_file_path)
        for logger in MyLogger._loggers:
            logger._logger.addHandler(logging.FileHandler(MyLogger._log_file_path))

    @staticmethod
    def enable_console_output():
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter(MyLogger._default_format))
        sh.setLevel(MyLogger._level)
        for logger in MyLogger._loggers:
            logger._logger.addHandler(sh)

    @staticmethod
    def mute_noisy_libs():
        for noisy_lib in ["urllib3", "selenium", "botocore", "undetected_chromedriver"]:
            logging.getLogger(noisy_lib).setLevel(logging.WARNING)


def getLogger(name):
    return MyLogger(name)
