import core.driver as driver
from core.log import getLogger
from core.track import track

from dotenv import load_dotenv
import os

import handlers.file_handlers.eshipper as eshipper_fh

import handlers.site_handlers.management.eshipper as eshipper_sh
import handlers.site_handlers.delivery.canadapost as canpost
import handlers.site_handlers.delivery.ups as ups
import handlers.site_handlers.delivery.canpar as canpar
import handlers.site_handlers.delivery.fedex as fdx
import handlers.site_handlers.delivery.purolator as puro

import testing.fc_testing as fc

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

        fc.test(sesh)

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