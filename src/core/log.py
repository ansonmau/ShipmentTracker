import logging
from datetime import datetime
import os
from core.utils import create_file

logging.basicConfig(
    format="%(asctime)s %(name)s: [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

class MyLogger:
    time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file_path = os.path.join("./logs", "log_{}.log".format(time))
    level = logging.INFO
    loggers = []

    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(MyLogger.level)
        MyLogger.loggers.append(self)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self ,msg):
        self.logger.warning(msg)

    def critical(self ,msg):
        self.logger.critical(msg)

    def debug(self ,msg):
        self.logger.debug(msg)

    def error(self ,msg):
        self.logger.error(msg)

    def set_level(self, level):
        self.logger.setLevel(level)

    @staticmethod
    def set_global_level(level):
        for logger in MyLogger.loggers:
            logger.set_level(level)

    @staticmethod
    def init_file_handler():
        create_file(MyLogger.log_file_path)
        for logger in MyLogger.loggers:
            logger.logger.addHandler(logging.FileHandler(MyLogger.log_file_path))

    def mute_noisy_libs(self):
        for noisy_lib in ["urllib3", "selenium", "botocore", "undetected_chromedriver"]:
            logging.getLogger(noisy_lib).setLevel(logging.WARNING)

def getLogger(name):
    return MyLogger(name)
