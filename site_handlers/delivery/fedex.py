from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from core.log import getLogger

logger = getLogger()

paths = {}

def scrape(sesh: WebDriverSession):
        sesh.get("https://www.purolator.com/en/shipping/tracker?pin=EWX000089623")
        pass 