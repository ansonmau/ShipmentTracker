from core.driver import WebDriverSession, ELEMENT_TYPES
from selenium.common.exceptions import StaleElementReferenceException
from os import getenv
from core.log import getLogger
from time import time
from core.track import result

logger = getLogger(__name__)

denied_cookies = False

class Paths:
        page = {
            "email_input": (ELEMENT_TYPES["id"], "sender_email"),
            "submit_btn": (ELEMENT_TYPES["id"], "submitButton"),
            "confirmation_dialog": (
                ELEMENT_TYPES["tag"],
                "trk-shared-get-status-updates-inline",
            ),
        }

        cookies = {
            "shadow_parent": (ELEMENT_TYPES["id"], "usercentrics-cmp-ui"),
            "deny_btn": (ELEMENT_TYPES["id"], "deny"),
        }

def executeScript(sesh: WebDriverSession, tracking_num):
    r = result(result.FAIL, carrier="Fedex", tracking_number=tracking_num)
    link = "https://www.fedex.com/fedextrack/?trknbr={}".format(tracking_num)
    sesh.get(link)

    removeCookiesBanner(sesh)

    sesh.input.path(Paths.page["email_input"], getenv("FEDEX_EMAIL"))
    sesh.click.path(Paths.page["submit_btn"])

    if not waitForConfirm(sesh):
        r.set_reason("Confirm button missing")
        return r

    r.set_result(result.SUCCESS)
    return r

def waitForConfirm(sesh: WebDriverSession, cd=3):
    end_time = time() + cd
    confirm_text = "Notification sent!"

    while time() < end_time:
        dialog = sesh.read.text(Paths.page["confirmation_dialog"])
        if confirm_text in dialog:
            return True

    return False


def removeCookiesBanner(sesh: WebDriverSession):
    global denied_cookies

    if denied_cookies:
        return

    shadow_parent = sesh.find.path(Paths.cookies["shadow_parent"])
    shadow_root = sesh.getShadowRoot(shadow_parent)

    sesh.click.fromParent(shadow_root, Paths.cookies["deny_btn"])

    denied_cookies = True
