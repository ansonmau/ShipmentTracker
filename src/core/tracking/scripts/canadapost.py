from src.core.tracking import track
from src.core.tracking.result import Result
from src.core.driver.locator import Locator, ElementTypes
from src.core.log import getLogger

from selenium.common.exceptions import StaleElementReferenceException
from os import getenv
from time import sleep

logger = getLogger("canada-post")

locators = {
    # ── general ───────────────────────────────────────────────────────────
    "get_email_notif":   Locator(ElementTypes.css, ".trackEmail"),
    "buttons":           Locator(ElementTypes.css, ".button"),
    # ── dialog box ────────────────────────────────────────────────────────
    "email_input":       Locator(ElementTypes.id, "emailAddressInput"),
    "add_email_btn":     Locator(ElementTypes.css, ".add"),
    "submit_btn":        Locator(ElementTypes.id, "submitButton"),
    # ── dialog types ────────────────────────────────────────────────────────
    "dialog_type_1":     Locator(ElementTypes.tag, "track-email-dialog"),
    "dialog_type_2":     Locator(ElementTypes.tag, "add-emails-dialog"),
    # ── checking ──────────────────────────────────────────────────────────
    "error_msg":         Locator(ElementTypes.id, "errorModal"),
    "tracking_status":   Locator(ElementTypes.tag, "track-expected-delivery"),
    "add_email_blocked": Locator(ElementTypes.css, ".disabled"),
    "list_of_packages":  Locator(ElementTypes.tag, "list-of-packages"),
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
        logger.debug("Error message (likely bot detection)")
        result.set_reason("Error message (likely bot detection)")
        return result

    if (check.notif_btn_missing()):
        # figure out why it's missing
        if (check.is_delivered()):
            msg = "Package already delivered"
        elif (check.no_associated_item()):
            msg = "Label not created yet (No associated number)"
        else:
            msg = "Notification button not found"
        logger.debug(f"Failed. reason: {msg}")
        result.set_reason(msg)
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

    # ─────────────────────────────< bot detect >─────────────────────────────
    def full_block(self):
        # can do a 1 sec wait here since it'll be perma on the screen when it does show up
        logger.debug("Searching for error box")
        full_block_modal = self.wds.find.element(locators['error_msg'], wait=1)

        if (full_block_modal is None) or (not full_block_modal.is_displayed()):
            logger.debug("... no error found")
            return False

        logger.debug("Error box detected. Attempting to get past it.")
        try:
            # attempt to click OK to get rid of it
            error_box = self.wds.find.element(locators['error_msg'])
            okay_button = self.wds.find.buttons_within(error_box, filter="OK")[0]
            self.wds.click.element(okay_button)
            sleep(2)
        
            if self.wds.find.element(locators['error_msg']):
                logger.debug("... attempt failed.")
                return True
            else:
                logger.debug("... success.")
                return False
        except:
            logger.debug("... failed.")
            pass 

        return True


    # ────────────────────────────< trackability >────────────────────────────
    def notif_btn_missing(self):
        """
        check for if notification button is missing
        """
        
        logger.debug("Searching for notification button")
        btn = self.wds.find.element(locators["get_email_notif"], wait = 3)
        if btn:
            logger.debug("... found")
            return False
        else:
            logger.debug("... missing")
            return True

    def is_delivered(self):
        """
        checks if delivered is in the status text
        """
        logger.debug("Checking delivery status")
        w = self.wds
        tracking_status = w.find.element(locators["tracking_status"], wait=1)

        if not tracking_status:
            logger.debug("... failed to find tracking status, skipping.")
            return False

        logger.debug("...delivery text located")
        if "delivered" in w.read.element_text( tracking_status ).lower():
            logger.debug("... already delivered")
            return True
        else:
            logger.debug("... not delivered yet")
            return False


    def no_associated_item(self):
        """
        - happens when label isn't created yet
        - checks if identifying text exists on the part of the page
        that contains shipment details. 
        """
        text_to_search = "item associated with this number"

        logger.debug("Checking if label is created")
        w = self.wds
        elm = w.find.element(locators["list_of_packages"], wait=1)

        if elm is None:
            logger.debug("... unable to locate element, skipping.")
            # assume its not due to this issue
            return False

        text = w.read.element_text(elm)
        if text_to_search in text:
            logger.debug("... not created")
            return True
        else:
            logger.debug("... created")
            return False

    # ───────────────────────────< In dialog box >─────────────────────────
    def dialog_is_loaded(self):
        return "Get email notifications" in self.dialog.get_text()

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
