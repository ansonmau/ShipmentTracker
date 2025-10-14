import core.driver as driver
from core.log import getLogger
from core.track import track
import core.utils as utils
import core.settings as settings

from dotenv import load_dotenv
import os

import handlers.file_handlers.eshipper as eshipper_fh

import handlers.site_handlers.management.eshipper as eshipper
import handlers.site_handlers.management.freightcom as freightcom
import handlers.site_handlers.management.ems as ems

import handlers.site_handlers.delivery.canadapost as canpost
import handlers.site_handlers.delivery.ups as ups
import handlers.site_handlers.delivery.canpar as canpar
import handlers.site_handlers.delivery.fedex as fdx
import handlers.site_handlers.delivery.purolator as puro

logger = getLogger(__name__)


def main():
    logger.info("initializing...")
    initialize.run()
    logger.info("Initialization complete")
    
    if settings.settings['clear_downloads']:
        cleanup.clearDLFolder()

    data = {
        "Canada Post": [],
        "Canpar": [],
        "Federal Express": [],
        "Purolator": [],
        "UPS": [],
    }

    report = {
            "success": [],
            "fail": [],
            "crash": [],
            }

    logger.info("starting web driver...")
    sesh = driver.WebDriverSession(undetected=True)
    
    if settings.settings['scrape']["freightcom"]:
        logger.info("looking through freightcom...")
        freightcom_data = freightcom.scrape(sesh)

        logger.debug("parsed data: {}".format(freightcom_data))
        utils.update_data(data, freightcom_data)

    if settings.settings['scrape']["ems"]:
        logger.info("looking through EMS...")
        ems_data = ems.scrape(sesh)

        logger.debug("parsed data: {}".format(ems_data))
        utils.update_data(data, ems_data)

    if settings.settings['scrape']["eshipper"]:
        logger.info("looking through eshipper...")
        eshipper.scrape(sesh)

        logger.debug("reading eshipper file")
        eshipper_data = eshipper_fh.parse()

        logger.debug("parsed data: {}".format(eshipper_data))
        utils.update_data(data, eshipper_data)

    logger.info("storing scraped data...")
    utils.save_data(data)

    if settings.settings['track']["canada post"]:
        logger.info("starting tracking for Canada Post shipments")
        logger.debug("Canada Post orders: {}".format(data["Canada Post"]))
        utils.update_data(report, track(sesh, "Canada Post", data["Canada Post"], canpost.executeScript))

    if settings.settings['track']["ups"]:
        logger.info("starting tracking for UPS shipments")
        logger.debug("UPS orders: {}".format(data["UPS"]))
        utils.update_data(report, track(sesh, "UPS", data["UPS"], ups.executeScript))

    if settings.settings['track']["canpar"]:
        logger.info("starting tracking for Canpar shipments")
        logger.debug("Canpar orders: {}".format(data["Canpar"]))
        utils.update_data(report, track(sesh, "Canpar", data["Canpar"], canpar.executeScript))

    if settings.settings['track']["purolator"]:
        logger.info("starting tracking for Purolator shipments")
        logger.debug("Purolator orders: {}".format(data["Purolator"]))
        utils.update_data(report, track(sesh, "Purolator", data["Purolator"], puro.executeScript))

    if settings.settings['track']["fedex"]:
        logger.info("starting tracking for Fedex shipments")
        logger.debug("Fedex orders: {}".format(data["Federal Express"]))
        utils.update_data(report, track(sesh, "Fedex", data["Federal Express"], fdx.executeScript))

    logger.info("Tracking complete. Saving results.")
    utils.save_report(report)

    logger.info("Starting clean up...")
    cleanup.run()
    logger.info("Clean up complete")

    return


class initialize:
    @staticmethod
    def run():
        logger.info("Loading keys...")
        initialize.loadEnvFile()

        logger.info("Creating downloads folder if it does not exist...")
        initialize.create_downloads_folder()

        logger.info("Creating data folder if it does not exist...")
        initialize.create_data_folder()

        logger.info("Creating reports folder if it does not exist...")
        initialize.create_reports_folder()
        
        logger.info("Creating logs folder if it does not exist...")
        initialize.create_logs_folder()

        logger.info("Loading settings...")
        initialize.load_settings()

    @staticmethod
    def create_downloads_folder():
        for dir_name in ['dls', 'dls_old']:
            utils.create_folder(dir_name)

    @staticmethod
    def create_data_folder():
        dir_name = "data"
        utils.create_folder(dir_name)

    @staticmethod
    def create_logs_folder():
        dir_name = "logs"
        utils.create_folder(dir_name)

    @staticmethod
    def create_reports_folder():
        dir_name = "reports"
        utils.create_folder(dir_name)
        
    @staticmethod
    def loadEnvFile():
        load_dotenv(dotenv_path="./data/keys.env")

    @staticmethod
    def load_settings():
        if settings.check_settings_exists():
            settings.load_settings() 
        else:
            logger.info("No settings file detected. Creating one with default settings...")
            settings.create_settings_file()
    
        
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
