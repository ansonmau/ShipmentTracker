from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from core.log import getLogger
from time import time as current_time

logger = getLogger(__name__)

paths = {
        "notify_me_btn": (ELEMENT_TYPES['id'], 'options-block_5f6a6725bde09-accordion-4-heading'),
        "notify_exception_toggle": (ELEMENT_TYPES['id'], 'notifyAtException'),
        "email_input": (ELEMENT_TYPES['id'], 'notifyList'),
        "add_notification_btn": (ELEMENT_TYPES['css'], '[onclick=\'doSubmit("addNotification");\']'),
        "notification_section": (ELEMENT_TYPES['id'], 'notifyContent')
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
        sesh.get('https://www.canpar.com/en/tracking/delivery_options.htm?barcode={}'.format(tracking_num))

        notify_me = sesh.find.path(paths['notify_me_btn'])
        sesh.scrollToElement(notify_me)
        sesh.click.element(notify_me)
        sesh.click.path(paths['notify_exception_toggle'])
        sesh.input.path(paths['email_input'], getenv('CANPAR_EMAIL'))
        sesh.click.path(paths['add_notification_btn'])

        waitForConfirm(sesh)

        return True

def waitForConfirm(sesh: WebDriverSession, cd = 10):
        confirmation_text = "Thank you. Notifications have been updated."

        end_time = current_time() + cd

        while current_time() < end_time:
                if sesh.read.text(paths['notification_section']) == confirmation_text:
                        return True
        
        return False

