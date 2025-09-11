import core.driver as driver
from core.log import getLogger
from core.track import track

from dotenv import load_dotenv
import os

import file_handlers.eshipper as eshipper_fh

import site_handlers.management.eshipper as eshipper_sh
import site_handlers.delivery.canadapost as canpost
import site_handlers.delivery.ups as ups
import site_handlers.delivery.canpar as canpar
import site_handlers.delivery.fedex as fdx
import site_handlers.delivery.purolator as puro

logger = getLogger(__name__)

def main():
        logger.info("initializing...")
        initialize.run()

        data = {
                "Canada Post": [],
                "Canpar": [],
                "Federal Express": [],
                "Purolator": [],
                "UPS": [],
        }

        reports = {}

        logger.info("starting web driver...")
        sesh = driver.WebDriverSession(undetected=True)

        logger.info("scraping eshipper for orders")
        eshipper_sh.scrape(sesh)
        
        logger.info("reading eshipper file")
        new_data = eshipper_fh.parse()
        logger.debug("parsed data: {}".format(new_data))
        
        logger.debug("updating data dict with new data: {}".format(new_data))
        data.update(new_data)

        logger.info("starting tracking for Canada Post shipments")
        logger.debug("Canada Post orders: {}".format(data['Canada Post']))
        reports["Canada Post"] = track(sesh, data['Canada Post'], canpost.executeScript)

        logger.info("starting tracking for UPS shipments")
        logger.debug("UPS orders: {}".format(data['UPS']))
        reports["UPS"] = track(sesh, data['UPS'], ups.executeScript)

        logger.info("starting tracking for Canpar shipments")
        logger.debug("Canpar orders: {}".format(data['Canpar']))
        reports["Canpar"] = track(sesh, data["Canpar"], canpar.executeScript)

        logger.info("starting tracking for Purolator shipments")
        logger.debug("Purolator orders: {}".format(data['Purolator']))
        reports["Purolator"] = track(sesh, data["Purolator"], puro.executeScript)

        logger.info("starting tracking for Fedex shipments")
        logger.debug("Fedex orders: {}".format(data['Federal Express']))
        reports["Fedex"] = track(sesh, data["Federal Express"], fdx.executeScript)

        logger.info("tracking complete. starting clean up.")
        cleanup.run()
        logger.info("clean up completed")
        
        return

class initialize:
        @staticmethod
        def run():
                logger.info("loading environment variables")
                initialize.loadEnvFile()

                logger.info("creating downloads folder if it does not exist")
                initialize.createDownloadsFolder()

                logger.info("creating data folder if it does not exist")
                initialize.createDataFolder()

        @staticmethod
        def createDownloadsFolder():
                dl_dir = os.path.abspath("./dls")
                os.makedirs(dl_dir, exist_ok=True)
        
        @staticmethod
        def createDataFolder():
                data_dir = os.path.abspath("./data")
                os.makedirs(data_dir, exist_ok=True)

        @staticmethod
        def loadEnvFile():
                load_dotenv(dotenv_path="./data/keys.env")
        
        @staticmethod
        def createLogFolder():
                log_dir = os.path.abspath("./logs")
                os.makedirs(log_dir, exist_ok=True)

class cleanup():
        @staticmethod
        def run():
                logger.info("clearing downloads folder")
                cleanup.clearDLFolder()

        @staticmethod
        def clearDLFolder():
                pass

if __name__ == "__main__":
        main()