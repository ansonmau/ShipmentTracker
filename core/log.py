import logging
from datetime import datetime
import os

log_dir = os.path.abspath("./logs")
os.makedirs(log_dir, exist_ok=True)

time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = os.path.join("./logs", "log_{}.log".format(time))

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s: [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename), 
        logging.StreamHandler() 
    ]
)

for noisy_lib in ["urllib3", "selenium", "botocore", "undetected_chromedriver"]:
        logging.getLogger(noisy_lib).setLevel(logging.WARNING)

def getLogger(name):
        return logging.getLogger(name)

