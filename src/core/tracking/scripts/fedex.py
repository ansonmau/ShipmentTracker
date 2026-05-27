from src.core.driver.locator import Locator, ElementTypes
from src.core.tracking.result import Result
from src.core.log import getLogger

from os import getenv
from time import time

logger = getLogger("fedex")

denied_cookies = False

class Locs:
        page = {
            "submit_btn": Locator(ElementTypes.id, "submitButton"),
            "confirmation_dialog": Locator(
                ElementTypes.tag,
                "trk-shared-get-status-updates-inline",
            ),
        }

        cookies = {
            "shadow_parent": Locator(ElementTypes.id, "usercentrics-cmp-ui"),
            "deny_btn": Locator(ElementTypes.id, "deny"),
        }

def executeScript(wds, tracking_num):
    r = Result(Result.FAIL, carrier="Fedex", tracking_number=tracking_num)
    link = "https://www.fedex.com/fedextrack/?trknbr={}".format(tracking_num)
    wds.nav.get(link)

    removeCookiesBanner(wds)

    wds.input.by_locator(Locs.page["email_input"], getenv("FEDEX_EMAIL"))
    wds.click.by_locator(Locs.page["submit_btn"])

    if not waitForConfirm(wds):
        r.set_reason("Confirm dialog missing")
        return r

    r.set_result(Result.SUCCESS)
    return r

def waitForConfirm(wds, wait=0):
    if (not wait):
        wait = wds.default_wait_time
    confirm_text = "Notification sent!"

    end_time = time() + wait
    while time() < end_time:
        dialog = wds.read.text(Locs.page["confirmation_dialog"])
        if confirm_text in dialog:
            return True

    return False


def removeCookiesBanner(wds):
    global denied_cookies

    if denied_cookies:
        return

    shadow_parent = wds.find.element(Locs.cookies["shadow_parent"])
    shadow_root = wds.misc.getShadowRoot(shadow_parent)

    wds.click.element_in_parent(shadow_root, Locs.cookies["deny_btn"])

    denied_cookies = True
