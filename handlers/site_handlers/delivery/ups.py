from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from core.log import getLogger
from core.track import result
import time

logger = getLogger(__name__)

class Paths:
    cookies_popup = (ELEMENT_TYPES["id"], "onetrust-consent-sdk")

    homepage = {
        "notify_me_btn": (ELEMENT_TYPES["id"], "stApp_btnSendMeUpdate"),
        }

    popup = {
        "continue_btn": (ELEMENT_TYPES["css"], ".ups-cta_primary"),
        "email_input_1": (ELEMENT_TYPES["id"], "stApp_pkgUpdatesEmailPhone0"),
        "email_input_2": (ELEMENT_TYPES["id"], "stApp_pkgUpdatesfailureEmail"),
        "done_btn": (ELEMENT_TYPES["id"], "stApp_sendUpdateDoneBtn"),
        "close_btn": (ELEMENT_TYPES["id"], "stApp_notiComplete_closeBtn"),
        }

    popup_options = {
        "update_option_1": (ELEMENT_TYPES["id"], "stApp_pkgUpdatesDelaylbl"),
        "update_option_2": (ELEMENT_TYPES["id"], "stApp_pkgUpdatesDeliveredlbl"),
        "update_option_3": (ELEMENT_TYPES["id"], "stApp_pkgUpdatesCurStatusLbl"),
        "update_option_4": (ELEMENT_TYPES["id"], "stApp_pkgUpdatesNotifyProblemLbl"),
        "update_option_5": (ELEMENT_TYPES["id"], "stApp_pkgUpdatesReadyPickuplbl"),
        }

def executeScript(sesh: WebDriverSession, tracking_num):
    r = result(result.FAIL, carrier="UPS", tracking_number=tracking_num)
    sesh.get("https://www.ups.com/track?trackingNumber={}".format(tracking_num))
    
    remove_cookies_popup(sesh)

    notify_btn = sesh.find.path(Paths.homepage["notify_me_btn"])
    sesh.scrollToElement(notify_btn, centered=True)
    time.sleep(1)
    sesh.click.element(notify_btn)

    sesh.click.path(Paths.popup["continue_btn"])

    elms_options = get_options(sesh)
    for elm in elms_options:
        sesh.click.element(elm)

    sesh.input.path(Paths.popup["email_input_1"], getenv("UPS_EMAIL1"))
    sesh.input.path(Paths.popup["email_input_2"], getenv("UPS_EMAIL2"))

    sesh.click.path(Paths.popup["done_btn"])
    sesh.click.path(Paths.popup["close_btn"])

    r.set_result(result.SUCCESS)
    return r
 
def remove_cookies_popup(sesh):
    elm_popup = sesh.find.path(Paths.cookies_popup)
    sesh.remove_element(elm_popup)

def get_options(sesh:WebDriverSession):
    opt_elm_list = []
    
    for opt_path in Paths.popup_options.values():
        elm_opt = sesh.find.path(opt_path, wait=2)
        if elm_opt:
            opt_elm_list.append(elm_opt)

    return opt_elm_list

            

