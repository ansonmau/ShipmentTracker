from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from core.log import getLogger
import time
from core.track import result

logger = getLogger(__name__)

class Driver():
    web_driver: WebDriverSession | None = None

    def set(self, sesh: WebDriverSession):
        Driver.web_driver = sesh

    def get(self) -> WebDriverSession:
        return self.web_driver

class Paths:

    page = {
        "tracking_info": (ELEMENT_TYPES["css"], ".results-container"),
        "progress_labels": (ELEMENT_TYPES['css'], ".progress-labels"),
        "active_classes": (ELEMENT_TYPES['css'], '.active')
    }

    chat = {
            "widget": (ELEMENT_TYPES["css"], '[aria-label=\"Chat Widget\"]'),
            "close_btn": (ELEMENT_TYPES["css"], '[aria-label="Close"]'),
            "confirm_close_btn": (ELEMENT_TYPES["id"], 'confirm-end-chat'),
    }

def executeScript(sesh: WebDriverSession, tracking_num):
    Driver().set(sesh)

    r = result(result.FAIL, carrier="Purolator", tracking_number=tracking_num)
    sesh.get(
        "https://www.purolator.com/en/shipping/tracker?pin={}".format(tracking_num)
    )
    removeCookiesBanner(sesh)

    if check_is_exception(sesh):
        r.set_reason("Shipment not ready to be tracked")
        return r

    if check_if_delivered():
        r.set_reason("Shipment already delivered [DNR]")
        return r

    e_tracking_details = sesh.find.path(Paths.page["tracking_info"])

    get_email_btn = sesh.find.links_within(e_tracking_details, filter="Get Email Notifications")
    sesh.click.element(get_email_btn[0])

    chat_handler = Chat_Handler(sesh)
    time.sleep(2)

    if "I can sign you up for email notifications" not in chat_handler.get_text():
        chat_handler.exit_chat()
        r.set_result(result.RETRY)
        return r

    chat_btn_name_buffer = []

    if "Before connecting you to one of our Customer Service Representative to look into this further" in chat_handler.get_text():
        chat_btn_name_buffer.append("No")
        chat_btn_name_buffer.append("Get updates")
    else:
        chat_btn_name_buffer.append("Agree to terms")
    
    for btn_name in chat_btn_name_buffer:
        sesh.click.element(chat_handler.get_button(btn_name))
        time.sleep(1)

    chat_btn_name_buffer.clear()
    
    time.sleep(1)
    if "Before connecting you to one of our Customer Service Representative to look into this further" in chat_handler.get_text():
        chat_btn_name_buffer.append("No")
        chat_btn_name_buffer.append("Get updates")

    chat_btn_name_buffer.append("Both")
    chat_btn_name_buffer.append("Only for myself")

    for btn_name in chat_btn_name_buffer:
        sesh.click.element(chat_handler.get_button(btn_name))
        time.sleep(1)
    
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
    
    r.set_result(result.SUCCESS)
    return r

def removeCookiesBanner(sesh: WebDriverSession):
    script = (
        "document.querySelector('[aria-label=\"Cookie Consent Banner\"]')?.remove();"
    )
    sesh.injectJS(script)

def check_is_exception(sesh: WebDriverSession) -> bool:
    return "Exceptions" in sesh.read.text(Paths.page['tracking_info'])

def check_if_delivered():
    sesh = Driver().get()
    # progress labels -> class = "active" -> text
    progress_labels = sesh.find.path(Paths.page['progress_labels'])
    active_class = sesh.find.fromParent(progress_labels, Paths.page['active_classes'])
    txt = sesh.read.textFromElement(active_class)
    logger.debug("progress label: {}".format(txt))

    return txt == "Delivered"

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

        assert len(search_results) == 1
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
