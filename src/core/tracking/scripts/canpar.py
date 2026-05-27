from src.core.driver.locator import Locator, ElementTypes
from src.core.log import getLogger
from src.core.tracking.result import Result

import time
from os import getenv

logger = getLogger("canpar")

locators = {
    "notify_me_btn": Locator(
        ElementTypes.id,
        "options-block_5f6a6725bde09-accordion-4-heading",
    ),
    "notify_exception_toggle": Locator(ElementTypes.css, '[for="notifyAtException"]'),
    "email_input": Locator(ElementTypes.id, "notifyList"),
    "add_notification_btn": Locator(
        ElementTypes.css,
        "[onclick='doSubmit(\"addNotification\");']",
    ),
    "notification_section": Locator(ElementTypes.id, "notifyContent"),
}

def executeScript(wds, tracking_num):
    r = Result(Result.FAIL, carrier="Canpar", tracking_number=tracking_num)

    wds.nav.get(
        "https://www.canpar.com/en/tracking/delivery_options.htm?barcode={}".format(
            tracking_num
        )
    )

    notify_me = wds.find.element(locators["notify_me_btn"])
    wds.click.element(notify_me)
    wds.misc.scrollToElement(notify_me)
    time.sleep(1)
    wds.click.by_locator(locators["notify_exception_toggle"])
    
    email_input_txt = "{}\n{}".format(getenv("CANPAR_EMAIL1"), getenv("CANPAR_EMAIL2")) 
    wds.input.by_locator(locators["email_input"], email_input_txt)
    wds.click.by_locator(locators["add_notification_btn"])

    if (not waitForConfirm(wds)):
        r.set_reason("Confirmation dialog failed to appear")
        return r

    r.set_result(Result.SUCCESS)
    return r


def waitForConfirm(wds, wait=0):
    if (not wait):
        wait = wds.default_wait_time

    confirmation_text = "Thank you. Notifications have been updated."
    end_time = time.time() + wait
    while time.time() < end_time:
        if wds.read.text(locators["notification_section"]) == confirmation_text:
            return True

    return False
