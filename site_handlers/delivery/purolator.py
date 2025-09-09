from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from core.log import getLogger
import time

logger = getLogger(__name__)

paths = {
        "tracking_details": (ELEMENT_TYPES['id'], 'tracking-details'),
        "buttons": (ELEMENT_TYPES['css'], '.btn'),
        "chat": (ELEMENT_TYPES['id'], 'chat'),
        "chat_messages": (ELEMENT_TYPES['tag'], 'p')
}

chat_paths = {
        "agree_tos": (ELEMENT_TYPES['css'], '[aria-label="Agree to terms"]'),
        "type_of_notif": (ELEMENT_TYPES['css'], '[aria-label="Both"]'),
        "notif_receiver": (ELEMENT_TYPES['css'], '[aria-label="Only for myself"]'),
        "name_input": (ELEMENT_TYPES['css'], '[name="name"]'),
        "email_input": (ELEMENT_TYPES['css'], '[name="email"]'),
        "submit_btn": (ELEMENT_TYPES['css'], '[aria-label="Submit"]'),
        "correct_btn": (ELEMENT_TYPES['css'], '[aria-label="Correct"]')
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
        sesh.get("https://www.purolator.com/en/shipping/tracker?pin={}".format(tracking_num))
        
        sesh.waitFor.path(paths['tracking_details'])

        removeCookiesBanner(sesh)

        btns = sesh.find.all(paths['buttons'])
        
        for btn in btns:
                if sesh.read.textFromElement(btn) == "Get Email Notifications":
                        email_notif_btn = btn
                        break
        
        sesh.click.element(email_notif_btn)
        
        chat_elmnt = sesh.find.path(paths['chat'], wait = 15) # sometimes takes a while for it to show up
        sesh.click.fromParent(chat_elmnt, chat_paths['agree_tos']) # *accept / do not accept
        sesh.click.fromParent(chat_elmnt, chat_paths['type_of_notif']) # delivery / exceptions / *both
        sesh.click.fromParent(chat_elmnt, chat_paths['notif_receiver']) # *for myself / for others

        sesh.input.fromParent(chat_elmnt, chat_paths['name_input'], getenv("PUROLATOR_NAME"))
        sesh.input.fromParent(chat_elmnt, chat_paths['email_input'], getenv("PUROLATOR_EMAIL"))
        sesh.click.fromParent(chat_elmnt, chat_paths['submit_btn'])
        sesh.click.fromParent(chat_elmnt, chat_paths['correct_btn'])

        waitForConfirm(sesh)

        return True

def waitForConfirm(sesh: WebDriverSession):
        timeout = 10
        end_time = time.time() + timeout

        chat = sesh.find.path(paths['chat'])
        verif_text = "I have completed your registration for Email Notifications"
        while time.time() < end_time:
                chat_msgs = sesh.find.allFromParent(chat, paths['chat_messages'])
                for msg in chat_msgs:
                        if verif_text in sesh.read.textFromElement(msg):
                                return True
        
        return False

def removeCookiesBanner(sesh: WebDriverSession):
        script = "document.querySelector('[aria-label=\"Cookie Consent Banner\"]')?.remove();"
        sesh.injectJS(script)