from src.core.tracking.result import Result
from src.core.driver.locator import Locator, ElementTypes
from src.core.log import getLogger

from selenium.common.exceptions import StaleElementReferenceException
from os import getenv
from time import sleep

logger = getLogger("canada-post")

locators = {
    "get_email_notif": Locator(ElementTypes.css, ".trackEmail"),
    "buttons": Locator(ElementTypes.css, ".button"),
    "email_input": Locator(ElementTypes.id, "emailAddressInput"),
    "add_email_btn": Locator(ElementTypes.css, ".add"),
    "add_email_blocked": Locator(ElementTypes.css, ".disabled"),
    "submit_btn": Locator(ElementTypes.id, "submitButton"),
    "dialog_type_1": Locator(ElementTypes.tag, "track-email-dialog"),
    "dialog_type_2": Locator(ElementTypes.tag, "add-emails-dialog"),
    "error_msg": Locator(ElementTypes.id, "errorModal"),
}

def executeScript(wds, tracking_num):
    result = Result()
    result.set_carrier("Canada Post")
    result.set_tracking_number(tracking_num)
    result.set_result(result.FAIL)

    check = StateCheck(wds)
    dialog = DialogHandler(wds)
    link = "https://www.canadapost-postescanada.ca/track-reperage/en#/search?searchFor={}".format(
        tracking_num
    )

    wds.nav.get(link)

    if (check.full_block()):
        result.set_reason("Error message (likely bot detection)")
        return result

    if (check.is_delivered()):
        result.set_reason("Package already delivered")
        return result
    
    if (not check.can_get_notifications()):
        result.set_reason("Notification button not found")
        return result

    wds.click.by_locator(locators["get_email_notif"])

    while (not check.dialog_is_loaded()):
        sleep(0.5)

    if (check.max_emails_reached()):
        result.set_reason("Maximum emails reached [DNR]")
        return result

    if (check.add_emails_dialog()):
        add_button = wds.find.buttons_within(dialog.get_current_dialog_element(), filter="Add")[0]
        wds.click.element(add_button)
        while (not check.dialog_is_loaded()):
            sleep(0.5)

    if (check.add_emails_button_blocked()):
        result.set_reason("3 or more emails already added [DNR]")
        return result

    wds.click.by_locator(locators["add_email_btn"])

    email_inputs = wds.find.all(locators["email_input"])
    if wds.read.element_text(email_inputs[0]) != "":
        result.set_reason("Email field already filled [DNR]")
        return result

    wds.input.element(email_inputs[0], getenv("CANADAPOST_EMAIL1"))
    wds.input.element(email_inputs[1], getenv("CANADAPOST_EMAIL2"))

    wds.click.by_locator(locators["submit_btn"])

    while (not check.dialog_is_loaded()):
        sleep(0.5)

    sleep(1) # needs time for button to load...? does not work without this pause
    ok_button = wds.find.buttons_within(dialog.get_current_dialog_element(), filter="OK")[0]
    wds.click.element(ok_button)
    
    result.set_result(Result.SUCCESS)
    return result


def getDialogText(wds):
    dialog_element = wds.find.element(locators["dialog_type_2"], wait=1)
    if dialog_element is None:
        dialog_element = wds.find.element(locators["dialog_type_1"])

    assert dialog_element is not None

    try:
        txt = wds.read.element_text(dialog_element)
    except StaleElementReferenceException:
        # for cases where the dialog element changes between me finding and reading it.
        txt = getDialogText(wds)

    return txt

def emailInputCountCheck(wds):
    input_elmnts = wds.find.all(locators["email_input"])
    return len(input_elmnts) > 2


def canAddEmails(wds):
    dialog = wds.find.element(locators["dialog_type_2"])  # will only check this in dialog 2
    add_blocked = wds.find.element_in_parent(dialog, locators["add_email_blocked"], wait=1)

    # element exists = cannot add new emails
    return False if add_blocked else True


def get_ok_button(wds):
    dialog = wds.find.element(locators["dialog_type_1"])
    if (dialog):
        ok_btn_lst = wds.find.buttons_within(dialog, filter="OK")
        return ok_btn_lst[0]
    return None

class DialogHandler:
    def __init__(self, wds):
        self.wds = wds
        self.driver = wds.driver 

    def get_current_dialog_element(self):
        dialog_element = None
        bFlip = False
        while (not(dialog_element)):
            bFlip = not bFlip
            if (bFlip):
                dialog_element = self.wds.find.element(locators["dialog_type_2"], wait=1)
            else:
                dialog_element = self.wds.find.element(locators["dialog_type_1"], wait=1)

        return dialog_element


    def get_text(self):
        txt = ''
        dialog_element = self.get_current_dialog_element()
 
        if (dialog_element):
            txt = self.wds.read.element_text(dialog_element)

        return txt
        

class StateCheck:
    def __init__(self, wds):
        self.wds = wds 
        self.driver = wds.driver 
        self.dialog = DialogHandler(wds)

    def full_block(self):
        full_block_modal = self.wds.find.element(locators['error_msg'])
        if (full_block_modal):
            if full_block_modal.is_displayed():
                error_box = self.wds.find.element(locators['error_msg'])
                okay_button = self.wds.find.buttons_within(error_box, filter="OK")[0]
                self.wds.click.element(okay_button)
                sleep(2)
            
                if self.wds.find.element(locators['error_msg']):
                    return 1
        return 0

    def can_get_notifications(self):
        return self.wds.wait.element_located(locators["get_email_notif"], wait = 3)

    def dialog_is_loaded(self):
        return "Get email notifications" in self.dialog.get_text()

    def is_delivered(self):
        # WIP
        return 0

    def max_emails_reached(self):
        if "reached the maximum" in self.dialog.get_text():
            return 1 
        return 0
    
    def add_emails_dialog(self):
        if "You can add or remove email addresses" in self.dialog.get_text():
            return 1
        return 0

    def add_emails_button_blocked(self):
        dialog = self.dialog.get_current_dialog_element()
        blocked = self.wds.find.element_in_parent(dialog, locators["add_email_blocked"], wait=1)

        return 1 if blocked else 0
