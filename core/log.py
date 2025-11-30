import logging
from datetime import datetime
import os
import core.utils as utils

class MyLogger:
    time = None
    log_filename = None
    log_init = False

    def init(self):
        utils.create_folder("logs")

        time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = os.path.join("./logs", "log_{}.log".format(time))

        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s %(name)s: [%(levelname)s] %(message)s",
            handlers=[logging.FileHandler(log_filename), logging.StreamHandler()],
        )

        for noisy_lib in ["urllib3", "selenium", "botocore", "undetected_chromedriver"]:
            logging.getLogger(noisy_lib).setLevel(logging.WARNING)

        MyLogger.log_init = True

    def getLogger(self,name):
        assert MyLogger.log_init
        return logging.getLogger(name)


def getLogger(name):
    if not MyLogger().log_init:
        MyLogger().init()
    return MyLogger().getLogger(name)
