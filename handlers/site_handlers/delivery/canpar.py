from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from core.log import getLogger
import time
from core.track import result

logger = getLogger(__name__)

paths = {
    "notify_me_btn": (
        ELEMENT_TYPES["id"],
        "options-block_5f6a6725bde09-accordion-4-heading",
    ),
    "notify_exception_toggle": (ELEMENT_TYPES["css"], '[for="notifyAtException"]'),
    "email_input": (ELEMENT_TYPES["id"], "notifyList"),
    "add_notification_btn": (
        ELEMENT_TYPES["css"],
        "[onclick='doSubmit(\"addNotification\");']",
    ),
    "notification_section": (ELEMENT_TYPES["id"], "notifyContent"),
}

def executeScript(sesh: WebDriverSession, tracking_num):
    r = result(result.FAIL, carrier="Canpar", tracking_number=tracking_num)
    sesh.get(
        "https://www.canpar.com/en/tracking/delivery_options.htm?barcode={}".format(
            tracking_num
        )
    )

    notify_me = sesh.find.path(paths["notify_me_btn"])
    sesh.click.element(notify_me)
    sesh.scrollToElement(notify_me)
    time.sleep(1)
    sesh.click.path(paths["notify_exception_toggle"])
    
    email_input_txt = "{}\n{}".format(getenv("CANPAR_EMAIL1"), getenv("CANPAR_EMAIL2")) 
    sesh.input.path(paths["email_input"], email_input_txt)
    sesh.click.path(paths["add_notification_btn"])

    waitForConfirm(sesh)

    r.set_result(result.SUCCESS)
    return r


def waitForConfirm(sesh: WebDriverSession, cd=10):
    confirmation_text = "Thank you. Notifications have been updated."

    end_time = time.time() + cd

    while time.time() < end_time:
        if sesh.read.text(paths["notification_section"]) == confirmation_text:
            return True

    return False
