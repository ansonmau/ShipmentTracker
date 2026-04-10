from dotenv import load_dotenv
from pathlib import Path

import core.driver.driver as driver
from core.log import getLogger, MyLogger
from core.track import track
import core.utils as utils
import core.settings as runtime_settings

import handlers.file_handlers.reports as report_handler
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
init_pass = True

def run(worker):
    from main import VERSION
    logger.info("Shipment Tracker version: {}".format(VERSION))

    initialize.run()
    cleanup.empty_dl_dir()

    if not init_pass:
        logger.critical("Initialization failed. Please review.")
        return 0

    logger.info("Initialization successful")

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
    wds = driver.WebDriverSession()
    wds.setUndetected(1)
    if (not wds.start()):
        return
    else:
        logger.info("Webdriver successfully started")

    logger.info("Reading settings")
    settings = runtime_settings.settings

    if settings['reuse_data']:
        logger.info("Importing previous data")
        utils.merge_dict_lists(data, utils.read_tracking_data())
    
    if settings['scrape']["freightcom"]:
        logger.info("Starting search through freightcom...")
        freightcom_data = freightcom.scrape(wds, worker)

        logger.debug("parsed data: {}".format(freightcom_data))
        utils.merge_dict_lists(data, freightcom_data)

    if settings['scrape']["ems"]:
        logger.info("looking through EMS...")
        ems_data = ems.scrape(wds)

        logger.debug("parsed data: {}".format(ems_data))
        utils.merge_dict_lists(data, ems_data)

    if settings['scrape']["eshipper"]:
        logger.info("looking through eshipper...")
        eshipper.scrape(wds)

        eshipper_data = eshipper_fh.parse()

        logger.debug("parsed data: {}".format(eshipper_data))
        utils.merge_dict_lists(data, eshipper_data)

    if settings['ignore_old']:
        duplicates_found = 0
        logger.info("Searching for previously tracked shipments")
        report_reader = report_handler.read()
        remove = []
        remove.extend(report_reader.successes())
        remove.extend([x for x in report_reader.fails() if "DNR" in x.reason])
        for result in remove:
            logger.debug("Checking shipment: {} {}".format(result.carrier, result.tracking_number))
            if result.tracking_number in data[result.carrier]:
                logger.debug("duplicate found: {} {}".format(result.carrier, result.tracking_number))
                duplicates_found+=1
                data[result.carrier].remove(result.tracking_number)
        logger.info("{} tracking numbers removed.".format(duplicates_found))

    logger.info("Storing scraped data...")
    utils.save_tracking_data(data)

    if settings['track']["canada post"]:
        logger.info("Starting tracking for Canada Post shipments")
        logger.debug("Canada Post orders: {}".format(data["Canada Post"]))
        cp_report = track(wds, "Canada Post", data["Canada Post"], canpost.executeScript)
        utils.merge_dict_lists(report, cp_report)

    if settings['track']["ups"]:
        logger.info("starting tracking for UPS shipments")
        logger.debug("UPS orders: {}".format(data["UPS"]))
        ups_report = track(wds, "UPS", data["UPS"], ups.executeScript)
        utils.merge_dict_lists(report, ups_report)

    if settings['track']["canpar"]:
        logger.info("starting tracking for Canpar shipments")
        logger.debug("Canpar orders: {}".format(data["Canpar"]))
        canpar_report = track(wds, "Canpar", data["Canpar"], canpar.executeScript)
        utils.merge_dict_lists(report, canpar_report)

    if settings['track']["purolator"]:
        logger.info("starting tracking for Purolator shipments")
        logger.debug("Purolator orders: {}".format(data["Purolator"]))
        puro_report = track(wds, "Purolator", data["Purolator"], puro.executeScript)
        utils.merge_dict_lists(report, puro_report)

    if settings['track']["fedex"]:
        logger.info("starting tracking for Fedex shipments")
        logger.debug("Fedex orders: {}".format(data["Fedex"]))
        fdx_report = track(wds, "Fedex", data["Fedex"], fdx.executeScript)
        utils.merge_dict_lists(report, fdx_report)

    logger.info("Tracking complete. Saving results.")
    report_handler.write_report(report)

    logger.info("Successes: {}".format(len(report['success'])))
    logger.info("Fails: {}".format(len(report['fail'])))
    logger.info("Crashes: {}".format(len(report['crash'])))

    logger.info("Starting clean up...")
    cleanup.run()
    logger.info("Clean up complete")

    return


class initialize:
    @staticmethod
    def run():
        logger.info("Loading keys...")
        initialize.init_env()

        logger.info("Initializing data...")
        initialize.init_data()

        logger.info("Initializing reports...")
        initialize.init_reports()
        
        logger.info("Initializing logs...")
        initialize.init_logs()

        logger.info("Initializing settings...")
        initialize.init_settings()

    @staticmethod
    def init_logs():
        MyLogger().init()

    @staticmethod
    def init_data():
        utils.create_folder(utils.PROJ_FOLDER / 'data')
        utils.create_folder(utils.PROJ_FOLDER / 'data' / 'dls')
        utils.create_file(utils.PROJ_FOLDER / 'data' / "delivery_data.json")
        utils.create_file(utils.PROJ_FOLDER / 'data' / "keys.env")

    @staticmethod
    def init_reports():
        dir_name = "reports"
        utils.create_folder(dir_name)
        
    @staticmethod
    def init_env():
        global init_pass
        init_pass = False

        env_path = utils.PROJ_FOLDER / "data" / "keys.env"

        if Path(env_path).stat().st_size == 0:
            logger.critical("Login keys empty. Please check data -> keys")
        else:
            load_dotenv(dotenv_path=env_path)
            init_pass = True

    @staticmethod
    def init_settings():
        global init_pass
        if runtime_settings.check_settings_exists():
            runtime_settings.load_settings() 
        else:
            logger.critical("No settings file detected. Creating one with default settings...")
            runtime_settings.create_settings_file()
            init_pass = False
            
        
class cleanup:
    @staticmethod
    def run():
        logger.info("Clearing downloads folder")
        cleanup.empty_dl_dir()

    @staticmethod
    def empty_dl_dir():
        ROOT = utils.PROJ_FOLDER 
        for file in (ROOT / 'data' / 'dls').iterdir():
            file.unlink()
