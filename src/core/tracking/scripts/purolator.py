import time
from os import getenv, name

from core.driver.locator import Locator, ElementTypes
from core.log import getLogger
from core.tracking.result import Result

logger = getLogger(__name__)

class Paths:

    page = {
        "tracking_info": Locator(ElementTypes.css, ".results-container"),
        "progress_labels": Locator(ElementTypes.css, ".progress-labels"),
        "active_classes": Locator(ElementTypes.css, '.active')
    }

    chat = {
            "widget": Locator(ElementTypes.css, '[aria-label=\"Chat Widget\"]'),
            "close_btn": Locator(ElementTypes.css, '[aria-label="Close"]'),
            "confirm_close_btn": Locator(ElementTypes.id, 'confirm-end-chat'),
    }

def executeScript(wds, tracking_num):
    r = Result(Result.FAIL, carrier="Purolator", tracking_number=tracking_num)
    wds.nav.get(
        "https://www.purolator.com/en/shipping/tracker?pin={}".format(tracking_num)
    )
    removeCookiesBanner(wds)

    if check_is_exception(wds):
        r.set_reason("Shipment not ready to be tracked")
        return r

    if check_if_delivered(wds):
        r.set_reason("Shipment already delivered [DNR]")
        return r

    e_tracking_details = wds.find.element(Paths.page["tracking_info"])

    get_email_btn = wds.find.links_within(e_tracking_details, filter="Get Email Notifications")
    wds.click.element(get_email_btn[0])

    chat_handler = Chat_Handler(wds)
    time.sleep(2)

    # check if bugged out and one is already in progress
    if "Please give me a moment while I retrieve the package status" in chat_handler.get_text():
        chat_handler.exit_chat()
        r.set_result(Result.RETRY)
        return r

    chat_btn_name_buffer = []

    if "Before connecting you to one of our Customer Service Representative to look into this further" in chat_handler.get_text():
        chat_btn_name_buffer.append("No")
        chat_btn_name_buffer.append("Get updates")
    else:
        chat_btn_name_buffer.append("Agree to terms")
    
    for btn_name in chat_btn_name_buffer:
        btn = chat_handler.get_button(btn_name)
        while btn == None:
            btn = chat_handler.get_button(btn_name)
        wds.click.element(chat_handler.get_button(btn_name))
        time.sleep(1)

    chat_btn_name_buffer.clear()
    
    time.sleep(1)
    if "Before connecting you to one of our Customer Service Representative to look into this further" in chat_handler.get_text():
        chat_btn_name_buffer.append("No")
        chat_btn_name_buffer.append("Get updates")

    chat_btn_name_buffer.append("Both")
    chat_btn_name_buffer.append("Only for myself")

    for btn_name in chat_btn_name_buffer:
        btn = chat_handler.get_button(btn_name)
        time.sleep(1)
        wds.click.element(chat_handler.get_button(btn_name))
    
    name_input = chat_handler.get_input("Name")
    email_input = chat_handler.get_input("Email")
    
    wds.input.element(name_input, getenv("PUROLATOR_NAME"))
    wds.input.element(email_input, getenv("PUROLATOR_EMAIL"))
    
    submit_btn = chat_handler.get_button('Submit')
    wds.click.element(submit_btn)

    correct_btn = chat_handler.get_button('Correct')
    wds.click.element(correct_btn)
    
    chat_handler.wait_for_confirm()

    chat_handler.exit_chat()
    
    r.set_result(Result.SUCCESS)
    return r

def removeCookiesBanner(wds):
    script = (
        "document.querySelector('[aria-label=\"Cookie Consent Banner\"]')?.remove();"
    )
    wds.misc.injectJS(script)

def check_is_exception(wds) -> bool:
    return "Exceptions" in wds.read.text(Paths.page['tracking_info'])

def check_if_delivered(wds):
    # progress labels -> class = "active" -> text
    progress_labels = wds.find.element(Paths.page['progress_labels'])
    active_class = wds.find.element_in_parent(progress_labels, Paths.page['active_classes'])
    txt = wds.read.element_text(active_class)
    logger.debug("progress label: {}".format(txt))

    return txt == "Delivered"

class Chat_Handler:
    def __init__(self, wds) -> None:
        self.wds = wds
        self.el_chat = self.get_chat_element()

    def get_chat_element(self):
        shadow_parent_loc = Locator(ElementTypes.css, '.shadow-dom')
        el_shadow_parent = self.wds.find.element(shadow_parent_loc)
        el_shadow_root = self.wds.misc.getShadowRoot(el_shadow_parent) 

        return self.wds.find.element_in_parent(el_shadow_root, Paths.chat['widget'])

    def get_button(self, btn_name):
        search_results = []
        end_time = time.time() + 5
        while len(search_results) == 0 and time.time() < end_time:
            search_results = self.wds.find.buttons_within(self.el_chat, btn_name)

        if len(search_results) == 0:
            return None

        return search_results[0]

    def get_input(self, input_name):
        result = None
        input_locator = Locator(ElementTypes.tag, 'input')

        search_results = []
        end_time = time.time() + 5
        while len(search_results) == 0 and time.time() < end_time:
            search_results = self.wds.find.all_in_parent(self.el_chat, input_locator)

        if len(search_results) <= 0:
            raise Exception("Failed to find input")

        filtered_results = self.wds.filter.by_attribute(search_results, "label", input_name)
        
        if (filtered_results):
            result = filtered_results[0]

        return result 

    def get_text(self):
        return self.wds.read.element_text(self.el_chat)

    def exit_chat(self):
        wds = self.wds
        
        close_btn = wds.find.element_in_parent(self.el_chat, Paths.chat["close_btn"])
        wds.click.element(close_btn)

        confirm_close_btn = wds.find.element_in_parent(self.el_chat, Paths.chat["confirm_close_btn"])
        wds.click.element(confirm_close_btn)
    
    def wait_for_confirm(self):
        timeout = 10
        end_time = time.time() + timeout

        verif_text = "I have completed your registration for Email Notifications"
        while time.time() < end_time:
            if verif_text in self.get_text():
                return True

        return False
