from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from core.log import getLogger
import time

logger = getLogger(__name__)

class Paths:

    page = {
        "tracking_info": (ELEMENT_TYPES["id"], "tracking-details"),
        "email_update_div": (ELEMENT_TYPES["css"], ".email-updates"),
        "buttons": (ELEMENT_TYPES["css"], ".btn"),
        "chat": (ELEMENT_TYPES["id"], "chat"),
        "chat_messages": (ELEMENT_TYPES["tag"], "p"),
    }

    chat = {
            "widget": (ELEMENT_TYPES["css"], "[aria-label]=\"Chat Widget\""),
            
    }

def executeScript(sesh: WebDriverSession, tracking_num):
    sesh.get(
        "https://www.purolator.com/en/shipping/tracker?pin={}".format(tracking_num)
    )

    sesh.waitFor.path(Paths.page["tracking_details"])

    removeCookiesBanner(sesh)

    btns = sesh.find.all(Paths.page["buttons"])

    for btn in btns:
        if sesh.read.textFromElement(btn) == "Get Email Notifications":
            email_notif_btn = btn
            break

    sesh.click.element(email_notif_btn)

    chat_btn_txts = ["Agree to terms", "Both", "Only for myself"]

    sesh.input.fromParent(
        chat_elmnt, Paths.chat["name_input"], getenv("PUROLATOR_NAME")
    )
    sesh.input.fromParent(
        chat_elmnt, Paths.chat["email_input"], getenv("PUROLATOR_EMAIL")
    )
    sesh.click.fromParent(chat_elmnt, Paths.chat["submit_btn"])
    sesh.click.fromParent(chat_elmnt, Paths.chat["correct_btn"])

    waitForConfirm(sesh)

    return True


def waitForConfirm(sesh: WebDriverSession):
    timeout = 10
    end_time = time.time() + timeout

    chat = sesh.find.path(Paths.page["chat"])
    verif_text = "I have completed your registration for Email Notifications"
    while time.time() < end_time:
        chat_msgs = sesh.find.allFromParent(chat, Paths.page["chat_messages"])
        for msg in chat_msgs:
            if verif_text in sesh.read.textFromElement(msg):
                return True

    return False


def removeCookiesBanner(sesh: WebDriverSession):
    script = (
        "document.querySelector('[aria-label=\"Cookie Consent Banner\"]')?.remove();"
    )
    sesh.injectJS(script)

def get_chat_button(sesh: WebDriverSession, btn_name):
    chat = sesh.find.path(Paths.chat["widget"])

    btn = sesh.find.buttons_within(chat, filter=btn_name)
    assert len(btn) == 1
    return btn[0]
    
