import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("output.log"), 
        logging.StreamHandler() 
    ]
)

def getLogger(name):
        return logging.getLogger(name)
