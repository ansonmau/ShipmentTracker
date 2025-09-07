import core.driver as driver
from core.log import getLogger

from dotenv import load_dotenv
import os

import file_handlers.eshipper as eshipper_fh

import site_handlers.management.eshipper as eshipper_sh
import site_handlers.delivery.canadapost as canpost
import site_handlers.delivery.ups as ups
import site_handlers.delivery.canpar as canpar
import site_handlers.delivery.purolator as puro

import testing.fedex_testing as fedex_test

logger = getLogger(__name__)

def main():
        logger.info("initializing...")
        initialize.run()
        data = {}

        logger.info("starting web driver...")
        sesh = driver.WebDriverSession(undetected=True)

        logger.info("scraping eshipper for orders")
        eshipper_sh.scrape(sesh)
        
        logger.info("reading eshipper file")
        new_data = eshipper_fh.parse()
        logger.debug("parsed data: {}".format(new_data))
        
        data.update(new_data)

        logger.info("starting tracking for canada post shipments")
        canpost.track(sesh, data['Canada Post'][5:])

        logger.info("starting tracking for UPS shipments")
        ups.track(sesh, data['UPS'])

        logger.info("starting tracking for Canpar shipments")
        canpar.track(sesh, data["Canpar"])

        logger.info("starting tracking for Purolator shipments")
        puro.track(sesh, data["Purolator"])

        logger.info("tracking complete. starting clean up.")
        cleanup.run()
        logger.info("executed successfully.")
        pass

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

class cleanup():
        @staticmethod
        def run():
                logger.info("clearing downloads folder")
                cleanup.clearDLFolder()

        @staticmethod
        def clearDLFolder():
                pass

if __name__ == "__main__":
        fedex_test.main()
        #main()