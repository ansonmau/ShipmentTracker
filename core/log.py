import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s: [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("output.log"), 
        logging.StreamHandler() 
    ]
)

logging.getLogger("undetected_chromedriver").setLevel(logging.WARNING)

def getLogger(name):
        return logging.getLogger(name)
