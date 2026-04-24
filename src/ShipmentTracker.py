import core.driver.driver as driver
from core.tracking.track import track
from core.tracking.report import Report
from core.tracking.result import Result
from core.settings import Settings
from core.init import Initializer
from core.log import getLogger
from core.tracking.dataHandler import Handler as TrackingDataHandler
from core.scraper.handler import Handler as ScraperHandler

import handlers.site_handlers.delivery.canadapost as canpost
import handlers.site_handlers.delivery.ups as ups
import handlers.site_handlers.delivery.canpar as canpar
import handlers.site_handlers.delivery.fedex as fdx
import handlers.site_handlers.delivery.purolator as puro

logger = getLogger("shipment tracker")

def run(worker):
    init            =   Initializer()
    report          =   Report()
    tdh             =   TrackingDataHandler()


    init_result = init.run()
    if (not init_result):
        logger.critical(f'Initialization failed. Please review.\nError code:\n{init.err_code}')
        return 1
    else:
        logger.info('Initialization successful')

    logger.info('Attempting to start web driver...')
    wds = driver.WebDriverSession()
    wds.setUndetected(True)
    session_start = wds.start()
    if (not(session_start)):
        return 1
    else:
        logger.info('Webdriver successfully started')
        wds.misc.maximize_window()

    settings = Settings.get_settings()

    if settings['reuse_data']:
        logger.info('Importing previous data')
        tdh.read_from_file()

    scraper = ScraperHandler(wds, tdh)
    scraper.set_worker(worker)
    scraper.run()

    if settings['ignore_already_tracked']:
        duplicates_found = 0
        logger.info('Searching for previously tracked shipments')

        old_reports = Report()
        old_reports.import_previous_reports()

        for result in old_reports.get_all():
            if (result.get_result() == Result.SUCCESS or "DNR" in result.get_reason()):
                t_num = result.get_tracking_number()
                carr = result.get_carrier()
                if tdh.check_shipment_exists(carr, t_num):
                    duplicates_found += 1
                    logger.debug('duplicate found: {} {}'.format(carr, t_num))
                    tdh.remove_shipment(carr, t_num)
        logger.info('{} tracking numbers removed.'.format(duplicates_found))

    logger.info('Storing scraped data...')
    tdh.save_to_file()

    if settings['track']['canada post']:
        logger.info('Starting tracking for Canada Post shipments')
        logger.debug('Canada Post shipments: {}'.format(tdh.get_tracking_numbers('Canada Post')))
        track(wds, 'Canada Post', tdh.get_tracking_numbers('Canada Post'), canpost.executeScript, report)

    if settings['track']['ups']:
        logger.info('Starting tracking for UPS shipments')
        logger.debug('UPS shipments: {}'.format(tdh.get_tracking_numbers('UPS')))
        track(wds, 'UPS', tdh.get_tracking_numbers('UPS'), ups.executeScript, report)

    if settings['track']['canpar']:
        logger.info('Starting tracking for Canpar shipments')
        logger.debug('Canpar shipments: {}'.format(tdh.get_tracking_numbers('Canpar')))
        track(wds, 'Canpar', tdh.get_tracking_numbers('Canpar'), canpar.executeScript, report)

    if settings['track']['purolator']:
        logger.info('Starting tracking for Purolator shipments')
        logger.debug('Purolator shipments: {}'.format(tdh.get_tracking_numbers('Purolator')))
        track(wds, 'Purolator', tdh.get_tracking_numbers('Purolator'), puro.executeScript, report)

    if settings['track']['fedex']:
        logger.info('Starting tracking for Fedex shipments')
        logger.debug('Fedex shipments: {}'.format(tdh.get_tracking_numbers('Fedex')))
        track(wds, 'Fedex', tdh.get_tracking_numbers('Fedex'), fdx.executeScript, report)

    logger.info('Tracking complete. Saving results.')
    report.save_to_file()

    logger.info('Successes: {}'.format(len(report.get_successes())))
    logger.info('Fails: {}'.format(len(report.get_fails())))
    logger.info('Crashes: {}'.format(len(report.get_crashes())))

    return 0
