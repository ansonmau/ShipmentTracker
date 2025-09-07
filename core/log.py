import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s: [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("output.log"), 
        logging.StreamHandler() 
    ]
)

for noisy_lib in ["urllib3", "selenium", "botocore", "undetected_chromedriver"]:
        logging.getLogger(noisy_lib).setLevel(logging.WARNING)

def getLogger(name):
        return logging.getLogger(name)
