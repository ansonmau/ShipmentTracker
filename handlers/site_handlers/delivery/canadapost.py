from core.track import result
from core.driver import WebDriverSession, ELEMENT_TYPES
from selenium.common.exceptions import StaleElementReferenceException
from os import getenv
from core.log import getLogger
from core.track import result

logger = getLogger(__name__)

paths = {
    "get_email_notif": (ELEMENT_TYPES["css"], ".trackEmail"),
    "buttons": (ELEMENT_TYPES["css"], ".button"),
    "email_input": (ELEMENT_TYPES["id"], "emailAddressInput"),
    "add_email_btn": (ELEMENT_TYPES["css"], ".add"),
    "add_email_blocked": (ELEMENT_TYPES["css"], ".disabled"),
    "submit_btn": (ELEMENT_TYPES["id"], "submitButton"),
    "dialog_type_1": (ELEMENT_TYPES["tag"], "track-email-dialog"),
    "dialog_type_2": (ELEMENT_TYPES["tag"], "add-emails-dialog"),
    "error_msg": (ELEMENT_TYPES["id"], "modalError"),
}


def executeScript(sesh: WebDriverSession, tracking_num):
    link = "https://www.canadapost-postescanada.ca/track-reperage/en#/search?searchFor={}".format(
        tracking_num
    )
    sesh.get(link)

    if not canGetNotifications(sesh):
        return result.FAIL

    sesh.click.path(paths["get_email_notif"])

    wait_dialog_load(sesh)
    dialog_txt = getDialogText(sesh)

    if "reached the maximum" in dialog_txt:
        return result.FAIL

    if "You can add or remove email addresses" in dialog_txt:
        passDialog1(sesh)
        wait_dialog_load(sesh)

    email_inputs = sesh.find.all(paths["email_input"])
    if len(email_inputs) == 1:
        if not canAddEmails(sesh):
            return result.FAIL
        sesh.click.path(paths["add_email_btn"])

    email_inputs = sesh.find.all(paths["email_input"])
    assert len(email_inputs) >= 2
    sesh.input.element(email_inputs[0], getenv("CANADAPOST_EMAIL1"))
    sesh.input.element(email_inputs[1], getenv("CANADAPOST_EMAIL2"))

    sesh.click.path(paths["submit_btn"])

    wait_dialog_load(sesh)

    ok_btn = get_ok_button(sesh)
    sesh.click.element(ok_btn)

    return result.SUCCESS


def getDialogText(sesh: WebDriverSession):
    dialog_element = sesh.find.path(paths["dialog_type_2"], wait=1)
    if dialog_element is None:
        dialog_element = sesh.find.path(paths["dialog_type_1"])

    assert dialog_element is not None

    try:
        txt = sesh.read.textFromElement(dialog_element)
    except StaleElementReferenceException:
        # for cases where the dialog element changes between me finding and reading it.
        txt = getDialogText(sesh)

    return txt


def wait_dialog_load(sesh: WebDriverSession):
    txt = getDialogText(sesh)
    while "Get email notifications" not in txt:
        txt = getDialogText(sesh)
    return


def passDialog1(sesh: WebDriverSession):
    wait_dialog_load(sesh)
    btns = sesh.filter.byText(sesh.find.all(paths["buttons"]), "Add")

    assert len(btns) == 1
    sesh.click.element(btns[0])


def emailInputCountCheck(sesh: WebDriverSession):
    input_elmnts = sesh.find.all(paths["email_input"])
    return len(input_elmnts) > 2


def canGetNotifications(sesh: WebDriverSession):
    if check_for_error_msg(sesh):
        return False

    get_notif_btn = sesh.find.path(paths["get_email_notif"], wait=3)
    if get_notif_btn is None:
        return False

    return True


def check_for_error_msg(sesh: WebDriverSession):
    return sesh.waitFor.path(paths["error_msg"], wait=1)


def canAddEmails(sesh: WebDriverSession):
    dialog = sesh.find.path(paths["dialog_type_2"])  # will only check this in dialog 2
    add_blocked = sesh.find.fromParent(dialog, paths["add_email_blocked"], wait=1)

    # element exists = cannot add new emails
    return False if add_blocked else True


def get_ok_button(sesh: WebDriverSession):
    dialog = sesh.find.path(paths["dialog_type_1"])

    assert dialog is not None
    ok_btn_lst = sesh.find.buttons_within(dialog, filter="OK")

    return ok_btn_lst[0]
