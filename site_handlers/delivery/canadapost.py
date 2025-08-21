from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from core.log import getLogger



def executeScript(sesh: WebDriverSession, tracking_nums):
        for tNum in tracking_nums:
                link = "https://www.canadapost-postescanada.ca/track-reperage/en#/search?searchFor={}".format(tNum)
                sesh.get(link)

