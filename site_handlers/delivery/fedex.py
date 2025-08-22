from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from core.log import getLogger
import time

logger = getLogger()

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

def scrape(sesh: WebDriverSession):
        sesh.get("https://www.purolator.com/en/shipping/tracker?pin=EWX000089623")
        
        sesh.waitFor(paths['tracking_details'])

        removeCookiesBanner(sesh)

        btns = sesh.findAll(paths['buttons'])
        
        for btn in btns:
                if sesh.getElementText(btn) == "Get Email Notifications":
                        email_notif_btn = btn
                        break
        
        sesh.element_click(email_notif_btn)
        
        sesh.waitFor(paths['chat'], wait = 15)
        sesh.click(chat_paths['agree_tos'])
        sesh.click(chat_paths['type_of_notif'])
        sesh.click(chat_paths['notif_receiver'])
        sesh.inputText(chat_paths['name_input'], getenv("PUROLATOR_NAME"))
        sesh.inputText(chat_paths['email_input'], getenv("PUROLATOR_EMAIL"))
        sesh.click(chat_paths['submit_btn'])
        sesh.click(chat_paths['correct_btn'])

        waitForConfirm(sesh)

def waitForConfirm(sesh: WebDriverSession):
        chat = sesh.find(paths['chat'])
        verif_text = "I have completed your registration for Email Notifications"

        timeout = 10
        end_time = time.time() + timeout

        confirmed = False
        while not confirmed and time.time() < end_time:
                chat_msgs = sesh.findFromParent(chat, paths['chat_messages'])
                for msg in chat_msgs:
                        if verif_text in msg.text:
                                return True
        
        return False

def removeCookiesBanner(sesh: WebDriverSession):
        script = "document.querySelector('[aria-label=\"Cookie Consent Banner\"]')?.remove();"
        sesh.injectJS(script)