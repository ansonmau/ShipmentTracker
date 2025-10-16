import logging
from datetime import datetime
import os
import core.utils as utils

utils.create_folder("logs")

time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = os.path.join("./logs", "log_{}.log".format(time))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s: [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(log_filename), logging.StreamHandler()],
)

for noisy_lib in ["urllib3", "selenium", "botocore", "undetected_chromedriver"]:
    logging.getLogger(noisy_lib).setLevel(logging.WARNING)


def getLogger(name):
    return logging.getLogger(name)
