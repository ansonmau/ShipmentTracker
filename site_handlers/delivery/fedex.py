from core.driver import WebDriverSession, ELEMENT_TYPES
from selenium.common.exceptions import StaleElementReferenceException
from os import getenv
from core.log import getLogger
from time import time

logger = getLogger(__name__)

denied_cookies = False


paths = {
        "email_input": (ELEMENT_TYPES['id'], 'sender_email'),
        "submit_btn": (ELEMENT_TYPES['id'], 'submitButton'),
        "confirmation_dialog": (ELEMENT_TYPES['tag'], 'trk-shared-get-status-updates-inline'),
}

cookie_banner_paths = {
        "shadow_parent": (ELEMENT_TYPES['id'], 'usercentrics-cmp-ui'),
        "deny_btn": (ELEMENT_TYPES['id'], 'deny')
}

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
                logger.debug("dialog text: {}".format(dialog))
                if confirm_text in dialog:
                        return True
        
        return False
        
def removeCookiesBanner(sesh: WebDriverSession):
        global denied_cookies

        if denied_cookies:
                return

        shadow_parent = sesh.find.path(cookie_banner_paths['shadow_parent'])
        shadow_root = sesh.getShadowRoot(shadow_parent)

        sesh.click.fromParent(shadow_root, cookie_banner_paths['deny_btn'])

        denied_cookies = True
