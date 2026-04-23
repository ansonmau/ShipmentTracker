from core.driver.driver import WebDriverSession
from core.driver.locator import Locator, ElementTypes

from os import getenv
from core.log import getLogger
from core.tracking.result import Result
import time

logger = getLogger(__name__)

class Locs:
    cookies_popup = Locator(ElementTypes.id, "onetrust-consent-sdk")

    homepage = {
        "notify_me_btn": Locator(ElementTypes.id, "stApp_btnSendMeUpdate"),
        }

    popup = {
        "continue_btn": Locator(ElementTypes.css, ".ups-cta_primary"),
        "email_input_1": Locator(ElementTypes.id, "stApp_pkgUpdatesEmailPhone0"),
        "email_input_2": Locator(ElementTypes.id, "stApp_pkgUpdatesfailureEmail"),
        "done_btn": Locator(ElementTypes.id, "stApp_sendUpdateDoneBtn"),
        "close_btn": Locator(ElementTypes.id, "stApp_notiComplete_closeBtn"),
        }

    popup_options = {
        "update_option_1": Locator(ElementTypes.id, "stApp_pkgUpdatesDelaylbl"),
        "update_option_2": Locator(ElementTypes.id, "stApp_pkgUpdatesDeliveredlbl"),
        "update_option_3": Locator(ElementTypes.id, "stApp_pkgUpdatesCurStatusLbl"),
        "update_option_4": Locator(ElementTypes.id, "stApp_pkgUpdatesNotifyProblemLbl"),
        "update_option_5": Locator(ElementTypes.id, "stApp_pkgUpdatesReadyPickuplbl"),
        }

def executeScript(wds, tracking_num):
    r = Result(Result.FAIL, carrier="UPS", tracking_number=tracking_num)
    wds.nav.get("https://www.ups.com/track?trackingNumber={}".format(tracking_num))
    
    remove_cookies_popup(wds)

    notify_btn = wds.find.element(Locs.homepage["notify_me_btn"])
    wds.misc.scrollToElement(notify_btn, centered=True)
    time.sleep(1)
    wds.click.element(notify_btn)

    wds.click.by_locator(Locs.popup["continue_btn"])

    elms_options = get_options(wds)
    for elm in elms_options:
        wds.click.element(elm)

    wds.input.by_locator(Locs.popup["email_input_1"], getenv("UPS_EMAIL1"))
    wds.input.by_locator(Locs.popup["email_input_2"], getenv("UPS_EMAIL2"))

    wds.click.by_locator(Locs.popup["done_btn"])
    wds.click.by_locator(Locs.popup["close_btn"])

    r.set_result(Result.SUCCESS)
    return r
 
def remove_cookies_popup(wds):
    elm_popup = wds.find.element(Locs.cookies_popup)
    wds.remove_element(elm_popup)

def get_options(wds):
    opt_elm_list = []
    
    for opt_locs in Locs.popup_options.values():
        elm_opt = wds.find.element(opt_locs, wait=2)
        if elm_opt:
            opt_elm_list.append(elm_opt)

    return opt_elm_list

            

