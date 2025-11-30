from pathlib import Path
from PySide6.QtCore import Signal, QObject
import core.driver as driver
from core.log import getLogger, MyLogger
from core.track import track
import core.utils as utils
import core.settings as settings
import handlers.file_handlers.reports as report_handler

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



class Worker:
    worker: QObject | None = None

    def set_worker(self, worker):
        Worker.worker = worker
    
    def stop(self):
        Worker.worker.stop_signal.emit()

    def pause(self):
        Worker.worker.pause_signal.emit()
        Worker.worker.pause_event.wait()
        Worker.worker.pause_signal.clear()
        

logger = getLogger(__name__)
init_pass = True

def run(worker):
    Worker().set_worker(worker)
    initialize.run()

    if not init_pass:
        logger.critical("Initialization failed. Please review.")
        return

    logger.info("Initialization successful")
    
    if settings.settings['clear_downloads']:
        logger.info("Clearing downloads folder...")
        cleanup.clearDLFolder()

    data = {
        "Canada Post": [],
        "Canpar": [],
        "Fedex": [],
        "Purolator": [],
        "UPS": []   
    }

    report = {
            "success": [],
            "fail": [],
            "crash": [],
            }

    logger.info("starting web driver...")
    sesh = driver.WebDriverSession(undetected=True)

    if settings.settings['reuse_data']:
        utils.merge_dict_lists(data, utils.read_tracking_data())
    
    if settings.settings['scrape']["freightcom"]:
        logger.info("looking through freightcom...")
        freightcom_data = freightcom.scrape(sesh, worker)

        logger.debug("parsed data: {}".format(freightcom_data))
        utils.merge_dict_lists(data, freightcom_data)

    if settings.settings['scrape']["ems"]:
        logger.info("looking through EMS...")
        ems_data = ems.scrape(sesh)

        logger.debug("parsed data: {}".format(ems_data))
        utils.merge_dict_lists(data, ems_data)

    if settings.settings['scrape']["eshipper"]:
        logger.info("looking through eshipper...")
        eshipper.scrape(sesh)

        logger.debug("reading eshipper file")
        eshipper_data = eshipper_fh.parse()

        logger.debug("parsed data: {}".format(eshipper_data))
        utils.merge_dict_lists(data, eshipper_data)

    duplicates_found = 0
    if settings.settings['ignore_old']:
        logger.info("Removing previously successfully tracked shipments...")
        remove = []
        remove.extend(report_handler.read.successes())
        remove.extend([x for x in report_handler.read.fails() if x.carrier=="Canada Post" and x.reason=="Maximum emails reached"])
        for result in remove:
            logger.debug("Attempting to remove shipment: {} {}".format(result.carrier, result.tracking_number))
            if result.tracking_number in data[result.carrier]:
                logger.debug("duplicate found: {} {}".format(result.carrier, result.tracking_number))
                duplicates_found+=1
                data[result.carrier].remove(result.tracking_number)
        logger.info("{} duplicates removed".format(duplicates_found))

    logger.info("storing scraped data...")
    utils.save_tracking_data(data)

    if settings.settings['track']["canada post"]:
        logger.info("starting tracking for Canada Post shipments")
        logger.debug("Canada Post orders: {}".format(data["Canada Post"]))
        cp_report = track(sesh, "Canada Post", data["Canada Post"], canpost.executeScript)
        utils.merge_dict_lists(report, cp_report)

    if settings.settings['track']["ups"]:
        logger.info("starting tracking for UPS shipments")
        logger.debug("UPS orders: {}".format(data["UPS"]))
        ups_report = track(sesh, "UPS", data["UPS"], ups.executeScript)
        utils.merge_dict_lists(report, ups_report)

    if settings.settings['track']["canpar"]:
        logger.info("starting tracking for Canpar shipments")
        logger.debug("Canpar orders: {}".format(data["Canpar"]))
        canpar_report = track(sesh, "Canpar", data["Canpar"], canpar.executeScript)
        utils.merge_dict_lists(report, canpar_report)

    if settings.settings['track']["purolator"]:
        logger.info("starting tracking for Purolator shipments")
        logger.debug("Purolator orders: {}".format(data["Purolator"]))
        puro_report = track(sesh, "Purolator", data["Purolator"], puro.executeScript)
        utils.merge_dict_lists(report, puro_report)

    if settings.settings['track']["fedex"]:
        logger.info("starting tracking for Fedex shipments")
        logger.debug("Fedex orders: {}".format(data["Fedex"]))
        fdx_report = track(sesh, "Fedex", data["Fedex"], fdx.executeScript)
        utils.merge_dict_lists(report, fdx_report)

    logger.info("Tracking complete. Saving results.")
    report_handler.write_report(report)

    logger.info("Starting clean up...")
    cleanup.run()
    logger.info("Clean up complete")
    sesh.endself()

    return


class initialize:
    @staticmethod
    def run():
        logger.info("Loading keys...")
        initialize.init_env()

        logger.info("Initializing downloads...")
        initialize.init_downloads()

        logger.info("Initializing data...")
        initialize.init_data()

        logger.info("Initializing reports...")
        initialize.init_reports()
        
        logger.info("Initializing logs...")
        MyLogger().init()

        logger.info("Initializing settings...")
        initialize.init_settings()

    @staticmethod
    def init_downloads():
        for dir_name in ['dls', 'dls_old']:
            utils.create_folder(dir_name)

    @staticmethod
    def init_data():
        dir_name = "data"
        utils.create_folder(dir_name)

    @staticmethod
    def init_reports():
        dir_name = "reports"
        utils.create_folder(dir_name)
        
    @staticmethod
    def init_env():
        global init_pass
        init_pass = False

        env_path = utils.PROJ_FOLDER / "data" / "keys.env"

        if not Path(env_path).exists():
            logger.critical("Login keys missing. Creating one...")
            utils.create_folder(utils.PROJ_FOLDER / "data")
            utils.create_file(env_path)
        elif Path(env_path).stat().st_size == 0:
            logger.critical("Login keys empty. Please check data -> keys")
        else:
            load_dotenv(dotenv_path=env_path)
            init_pass = True

    @staticmethod
    def init_settings():
        global init_pass
        if settings.check_settings_exists():
            settings.load_settings() 
        else:
            logger.critical("No settings file detected. Creating one with default settings...")
            settings.create_settings_file()
            init_pass = False
            
    
        
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
        src = os.path.abspath(utils.PROJ_FOLDER / 'dls')
        dst = os.path.abspath(utils.PROJ_FOLDER / 'dls_old')
        
        for file in os.listdir(src):
            og_file = os.path.join(src, file)
            dst_file = os.path.join(dst, file)
            if os.path.isfile(og_file):
                shutil.move(og_file, dst_file)
        pass
