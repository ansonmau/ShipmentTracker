from core.driver import WebDriverSession, ELEMENT_TYPES
from selenium.common.exceptions import StaleElementReferenceException
from os import getenv
from core.log import getLogger
from time import time

logger = getLogger(__name__)

denied_cookies = False


paths = {
        "deny_cookies_btn": (ELEMENT_TYPES['css'], '.uc-deny-button'),
        "email_input": (ELEMENT_TYPES['id'], 'sender_email'),
        "submit_btn": (ELEMENT_TYPES['id'], 'submitButton'),
        "confirmation_dialog": (ELEMENT_TYPES['tag'], 'trk-shared-get-status-updates-inline')
}

def track(sesh: WebDriverSession, tracking_nums):
        report = {
                "success": [],
                "fail": []
        }

        for tracking_num in tracking_nums:
                if executeScript(sesh, tracking_num):
                        report['success'].append(tracking_num)
                else:
                        report['fail'].append(tracking_num)

        return report

def executeScript(sesh: WebDriverSession, tracking_num):
        link = "https://www.fedex.com/fedextrack/?trknbr={}".format(tracking_num)
        sesh.get(link)

        removeCookiesBanner(sesh)

        sesh.input.path(paths['email_input'], getenv("FEDEX_EMAIL"))
        sesh.click.path(paths['submit_btn'])

        return waitForConfirm(sesh)

def waitForConfirm(sesh: WebDriverSession, cd = 3):
        end_time = time() + cd
        confirm_text = "Notification sent!"

        while time() < end_time:
                dialog = sesh.read.text(paths['confirmation_dialog'])
                logger.debug("dialog text: {}".format())
                if dialog == confirm_text:
                        return True
        
        return False
        
def removeCookiesBanner(sesh: WebDriverSession):
        global denied_cookies

        if not denied_cookies:
                sesh.click.path(paths['deny_cookies_btn'])
                denied_cookies = True
