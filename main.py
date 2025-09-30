import core.driver as driver
from core.log import getLogger
from core.track import track
import core.utils as utils

from dotenv import load_dotenv
import os

import handlers.file_handlers.eshipper as eshipper_fh

import handlers.site_handlers.management.eshipper as eshipper
import handlers.site_handlers.management.freightcom as freightcom

import handlers.site_handlers.delivery.canadapost as canpost
import handlers.site_handlers.delivery.ups as ups
import handlers.site_handlers.delivery.canpar as canpar
import handlers.site_handlers.delivery.fedex as fdx
import handlers.site_handlers.delivery.purolator as puro

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

    logger.info("looking through eshipper...")
    eshipper.scrape(sesh)

    logger.debug("reading eshipper file")
    eshipper_data = eshipper_fh.parse()

    logger.debug("parsed data: {}".format(eshipper_data))
    utils.update_data(data, eshipper_data)

    logger.info("looking through freightcom...")
    freightcom_data = freightcom.scrape(sesh)

    logger.debug("parsed data: {}".format(freightcom_data))
    utils.update_data(data, freightcom_data)

    logger.info("starting tracking for Canada Post shipments")
    logger.debug("Canada Post orders: {}".format(data["Canada Post"]))
    reports["Canada Post"] = track(sesh, data["Canada Post"], canpost.executeScript)

    logger.info("starting tracking for UPS shipments")
    logger.debug("UPS orders: {}".format(data["UPS"]))
    reports["UPS"] = track(sesh, data["UPS"], ups.executeScript)

    logger.info("starting tracking for Canpar shipments")
    logger.debug("Canpar orders: {}".format(data["Canpar"]))
    reports["Canpar"] = track(sesh, data["Canpar"], canpar.executeScript)

    logger.info("starting tracking for Purolator shipments")
    logger.debug("Purolator orders: {}".format(data["Purolator"]))
    reports["Purolator"] = track(sesh, data["Purolator"], puro.executeScript)

    logger.info("starting tracking for Fedex shipments")
    logger.debug("Fedex orders: {}".format(data["Federal Express"]))
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
        for dir_name in ['./dls', './dls_old']:
            dl_dir = os.path.abspath(dir_name)
            os.makedirs(dl_dir, exist_ok=True)

    @staticmethod
    def createDataFolder():
        data_dir = os.path.abspath("./data")
        os.makedirs(data_dir, exist_ok=True)

    @staticmethod
    def loadEnvFile():
        load_dotenv(dotenv_path="./data/keys.env")


class cleanup:
    @staticmethod
    def run():
        logger.info("clearing downloads folder")
        cleanup.clearDLFolder()

    @staticmethod
    def clearDLFolder():
        """ 
        desc: moves files in dl folder to old_dls.
        purpose: makes reading the newest downloads easier
        """
        import shutil
        src = os.path.abspath("./dls")
        dst = os.path.abspath("./dls_old")
        
        for file in os.listdir(src):
            og_file = os.path.join(src, file)
            dst_file = os.path.join(dst, file)
            if os.path.isfile(og_file):
                shutil.move(og_file, dst_file)
        pass


if __name__ == "__main__":
    main()
