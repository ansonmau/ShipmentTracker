import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("output.log"), 
        logging.StreamHandler() 
    ]
)

def getLogger():
        return logging.getLogger(__name__)
