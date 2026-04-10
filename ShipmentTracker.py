import core.driver.driver as driver
from core.tracking.track import track
from core.tracking.report import Report
from core.tracking.result import Result
from core.utils import ROOT, save_tracking_data, merge_dict_lists, read_tracking_data
from core.settings import Settings
from core.init import Initializer
from core.log import getLogger

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

def run(worker):
    from main import VERSION
    logger.info('Shipment Tracker version: {}'.format(VERSION))

    init = Initializer()
    if (not init.run()):
        logger.critical(f'Initialization failed. Please review. Error code:\n{init.err_code}')
        return 0
    logger.info('Initialization successful')

    cleanup.empty_dl_dir()

    data = {
        'Canada Post': [],
        'Canpar': [],
        'Fedex': [],
        'Purolator': [],
        'UPS': []   
    }

    report = Report()

    logger.info('starting web driver...')
    wds = driver.WebDriverSession()
    wds.setUndetected(1)
    if (not wds.start()):
        return
    else:
        logger.info('Webdriver successfully started')

    logger.info('Reading settings')
    settings = Settings.get_settings()

    if settings['reuse_data']:
        logger.info('Importing previous data')
        merge_dict_lists(data, read_tracking_data())
    
    if settings['scrape']['freightcom']:
        logger.info('Searching through Freightcom for shipment information...')
        freightcom_data = freightcom.scrape(wds, worker)

        logger.debug('parsed data: {}'.format(freightcom_data))
        merge_dict_lists(data, freightcom_data)

    if settings['scrape']['ems']:
        logger.info('Searching through EMS for shipment information...')
        ems_data = ems.scrape(wds)

        logger.debug('parsed data: {}'.format(ems_data))
        merge_dict_lists(data, ems_data)

    if settings['scrape']['eshipper']:
        logger.info('Searching through EShipper for shipment information...')
        eshipper.scrape(wds)

        eshipper_data = eshipper_fh.parse()

        logger.debug('parsed data: {}'.format(eshipper_data))
        merge_dict_lists(data, eshipper_data)

    if settings['ignore_old']:
        duplicates_found = 0
        logger.info('Searching for previously tracked shipments')

        old_reports = Report()
        old_reports.import_previous_reports()

        for result in old_reports.get_all():
            if (result.get_result() == Result.SUCCESS or "DNR" in result.get_reason()):
                t_num = result.get_tracking_number()
                carr = result.get_carrer()
                if (t_num in data[carr]):
                    logger.debug('duplicate found: {} {}'.format(carr, t_num))
                    duplicates_found += 1
                    data[carr].remove(t_num)

        logger.info('{} tracking numbers removed.'.format(duplicates_found))

    logger.info('Storing scraped data...')
    save_tracking_data(data)

    if settings['track']['canada post']:
        logger.info('Starting tracking for Canada Post shipments')
        logger.debug('Canada Post orders: {}'.format(data['Canada Post']))
        track(wds, 'Canada Post', data['Canada Post'], canpost.executeScript, report)

    if settings['track']['ups']:
        logger.info('Starting tracking for UPS shipments')
        logger.debug('UPS orders: {}'.format(data['UPS']))
        track(wds, 'UPS', data['UPS'], ups.executeScript, report)

    if settings['track']['canpar']:
        logger.info('Starting tracking for Canpar shipments')
        logger.debug('Canpar orders: {}'.format(data['Canpar']))
        track(wds, 'Canpar', data['Canpar'], canpar.executeScript, report)

    if settings['track']['purolator']:
        logger.info('Starting tracking for Purolator shipments')
        logger.debug('Purolator orders: {}'.format(data['Purolator']))
        track(wds, 'Purolator', data['Purolator'], puro.executeScript, report)

    if settings['track']['fedex']:
        logger.info('Starting tracking for Fedex shipments')
        logger.debug('Fedex orders: {}'.format(data['Fedex']))
        track(wds, 'Fedex', data['Fedex'], fdx.executeScript, report)

    logger.info('Tracking complete. Saving results.')
    report_handler.write_report(report)

    logger.info('Successes: {}'.format(len(report.get_successes())))
    logger.info('Fails: {}'.format(len(report.get_fails())))
    logger.info('Crashes: {}'.format(len(report.get_crashes())))

    logger.info('Starting clean up...')
    cleanup.run()
    logger.info('Clean up complete')

    return


class cleanup:
    @staticmethod
    def run():
        logger.info('Clearing downloads folder')
        cleanup.empty_dl_dir()

    @staticmethod
    def empty_dl_dir():
        for file in (ROOT / 'data' / 'dls').iterdir():
            file.unlink()
