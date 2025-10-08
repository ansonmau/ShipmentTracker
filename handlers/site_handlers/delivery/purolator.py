from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from core.log import getLogger
import time
from core.track import result

logger = getLogger(__name__)

class Paths:

    page = {
        "tracking_info": (ELEMENT_TYPES["id"], "tracking-detail"),
    }

    chat = {
            "widget": (ELEMENT_TYPES["css"], '[aria-label=\"Chat Widget\"]'),
            "close_btn": (ELEMENT_TYPES["css"], '[aria-label="Close"]'),
            "confirm_close_btn": (ELEMENT_TYPES["id"], 'confirm-end-chat'),
    }

def executeScript(sesh: WebDriverSession, tracking_num):
    sesh.get(
        "https://www.purolator.com/en/shipping/tracker?pin={}".format(tracking_num)
    )

    e_tracking_details = sesh.find.path(Paths.page["tracking_info"])

    removeCookiesBanner(sesh)
    get_email_btn = sesh.find.links_within(e_tracking_details, filter="Get Email Notifications")

    sesh.click.element(get_email_btn[0])

    chat_handler = Chat_Handler(sesh)
    chat_btn_txts = ["Agree to terms", "Both", "Only for myself"]
    for btn_name in chat_btn_txts:
        curr_btn = chat_handler.get_button(btn_name)
        sesh.click.element(curr_btn)
    
    name_input = chat_handler.get_input("Name")
    email_input = chat_handler.get_input("Email")
    
    sesh.input.element(name_input, getenv("PUROLATOR_NAME"))
    sesh.input.element(email_input, getenv("PUROLATOR_EMAIL"))
    
    submit_btn = chat_handler.get_button('Submit')
    sesh.click.element(submit_btn)

    correct_btn = chat_handler.get_button('Correct')
    sesh.click.element(correct_btn)
    
    chat_handler.wait_for_confirm()
    chat_handler.exit_chat()
    
    return result.SUCCESS

def removeCookiesBanner(sesh: WebDriverSession):
    script = (
        "document.querySelector('[aria-label=\"Cookie Consent Banner\"]')?.remove();"
    )
    sesh.injectJS(script)

class Chat_Handler:
    def __init__(self, sesh: WebDriverSession) -> None:
        self.sesh = sesh
        self.el_chat = self.get_chat_element()

    def get_chat_element(self):
        shadow_parent_loc = (ELEMENT_TYPES["css"], '.shadow-dom')
        el_shadow_parent = self.sesh.find.path(shadow_parent_loc)
        el_shadow_root = self.sesh.getShadowRoot(el_shadow_parent) 

        return self.sesh.find.fromParent(el_shadow_root, Paths.chat['widget'])

    def get_button(self, btn_name):
        search_results = []
        end_time = time.time() + 5
        while len(search_results) == 0 and time.time() < end_time:
            search_results = self.sesh.find.buttons_within(self.el_chat, btn_name)

        assert len(search_results) > 0
        return search_results[0]

    def get_input(self, input_name):
        input_locator = (ELEMENT_TYPES['tag'], 'input')

        search_results = []
        end_time = time.time() + 5
        while len(search_results) == 0 and time.time() < end_time:
            search_results = self.sesh.find.allFromParent(self.el_chat, input_locator)

        assert len(search_results) > 0
        filtered_results = self.sesh.filter.byAttribute(search_results, "label", input_name)

        assert len(filtered_results) > 0
        return filtered_results[0]

    def get_text(self):
        return self.sesh.read.textFromElement(self.el_chat)

    def exit_chat(self):
        sesh = self.sesh
        
        close_btn = sesh.find.fromParent(self.el_chat, Paths.chat["close_btn"])
        sesh.click.element(close_btn)

        confirm_close_btn = sesh.find.fromParent(self.el_chat, Paths.chat["confirm_close_btn"])
        sesh.click.element(confirm_close_btn)
    
    def wait_for_confirm(self):
        timeout = 10
        end_time = time.time() + timeout

        verif_text = "I have completed your registration for Email Notifications"
        while time.time() < end_time:
            if verif_text in self.get_text():
                return True

        return False
