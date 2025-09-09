from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from core.log import getLogger

logger = getLogger(__name__)

paths = {
        "notify_me_btn": (ELEMENT_TYPES['id'], 'stApp_btnSendMeUpdate'),
        "continue_btn": (ELEMENT_TYPES['css'], '.ups-cta_primary'),
        "update_option_1": (ELEMENT_TYPES['id'], 'stApp_pkgUpdatesDelaylbl'),
        "update_option_2": (ELEMENT_TYPES['id'], 'stApp_pkgUpdatesDeliveredlbl'),
        "update_option_3": (ELEMENT_TYPES['id'], 'stApp_pkgUpdatesCurStatusLbl'),
        "email_input_1": (ELEMENT_TYPES['id'], 'stApp_pkgUpdatesEmailPhone0'),
        "update_option_4": (ELEMENT_TYPES['id'], 'stApp_pkgUpdatesNotifyProblemLbl'),
        "email_input_2": (ELEMENT_TYPES['id'], 'stApp_pkgUpdatesfailureEmail'),
        "done_btn": (ELEMENT_TYPES['id'], 'stApp_sendUpdateDoneBtn'),
        "close_btn": (ELEMENT_TYPES['id'], 'stApp_notiComplete_closeBtn'),
}

def track(sesh: WebDriverSession, tracking_nums):
        report = {
                "success": [],
                "fail": [],
                "crash": []
        }

        for tracking_num in tracking_nums:
                try:
                        if executeScript(sesh, tracking_num):
                                report['success'].append(tracking_num)
                        else:
                                report['fail'].append(tracking_num)
                except Exception as e:
                        logger.warning("(#{}) Unknown error: {}".format(tracking_num, e))
                        report['crash'].append(tracking_num)

        return report

def executeScript(sesh: WebDriverSession, tracking_num):
        sesh.get('https://www.ups.com/WebTracking?trackingNumber={}'.format(tracking_num))
        
        notify_btn = sesh.find.path(paths['notify_me_btn'])
        sesh.scrollToElement(notify_btn)
        sesh.click.element(notify_btn)
        sesh.click.path(paths['continue_btn'])
        sesh.click.path(paths['update_option_1'])
        sesh.click.path(paths['update_option_2'])
        sesh.click.path(paths['update_option_3'])
        sesh.click.path(paths['update_option_4'])
        sesh.input.path(paths['email_input_1'], getenv('UPS_EMAIL1'))
        sesh.input.path(paths['email_input_2'], getenv('UPS_EMAIL2'))
        sesh.click.path(paths['done_btn'])
        sesh.waitFor.path(paths['close_btn'])

        return True

