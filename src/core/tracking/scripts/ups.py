from src.core.driver.driver import WebDriverSession
from src.core.driver.locator import Locator, ElementTypes

from os import getenv
from src.core.log import getLogger
from src.core.tracking.result import Result
from time import sleep

logger = getLogger("ups")

# ╭──────────────────────────────────────────────────────────╮
# │                        Locations                         │
# ╰──────────────────────────────────────────────────────────╯
class Locs:
    cookies_popup =         Locator(ElementTypes.id, "onetrust-consent-sdk")

    homepage = {
        "notify_me_btn":    Locator(ElementTypes.id, "stApp_btnSendMeUpdate"),
        "title_card":       Locator(ElementTypes.css, ".card-header")
        }

    popup = {
        "container":        Locator(ElementTypes.css, ".modal-content"),
        "email_input_1":    Locator(ElementTypes.id,  "stApp_pkgUpdatesEmailPhone0"),
        "email_input_2":    Locator(ElementTypes.id,  "stApp_pkgUpdatesfailureEmail"),
        "done_btn":         Locator(ElementTypes.id,  "stApp_sendUpdateDoneBtn"),
        "close_btn":        Locator(ElementTypes.id,  "stApp_notiComplete_closeBtn"),
        }

    popup_options = {
        "update_option_1":  Locator(ElementTypes.id, "stApp_pkgUpdatesCurStatusLbl"),
        "update_option_2":  Locator(ElementTypes.id, "stApp_pkgUpdatesDeliveredlbl"),
        "update_option_3":  Locator(ElementTypes.id, "stApp_pkgUpdatesDelaylbl"),
        "update_option_4":  Locator(ElementTypes.id, "stApp_pkgUpdatesNotifyProblemLbl"),
        "update_option_5":  Locator(ElementTypes.id, "stApp_pkgUpdatesReadyPickuplbl"),
        }

# ╭──────────────────────────────────────────────────────────╮
# │                 Fail check helper class                  │
# ╰──────────────────────────────────────────────────────────╯
class Check:
    def __init__(self, wds: WebDriverSession):
        self._wds = wds

    def already_delivered(self):
        # check if title card says delivered in it
        check_txt  =   "delivered"
        title_card =   self._wds.find.element(Locs.homepage["title_card"])

        if (title_card):
            title_card_text = self._wds.read.element_text(title_card).lower()
            return check_txt in title_card_text
        else:
            return False

# ╭──────────────────────────────────────────────────────────╮
# │                     helper functions                     │
# ╰──────────────────────────────────────────────────────────╯
def _remove_cookies_popup(wds):
    elm_popup = wds.find.element(Locs.cookies_popup)
    wds.misc.remove_element(elm_popup)

def _get_options(wds):
    opt_elm_list = []
    
    for opt_locs in Locs.popup_options.values():
        elm_opt = wds.find.element(opt_locs, wait=2)
        if elm_opt:
            opt_elm_list.append(elm_opt)

    return opt_elm_list

# ╭──────────────────────────────────────────────────────────╮
# │                       Main script                        │
# ╰──────────────────────────────────────────────────────────╯
def executeScript(wds, tracking_num):
    r = Result(Result.FAIL, carrier="UPS", tracking_number=tracking_num)
    wds.nav.get("https://www.ups.com/track?trackingNumber={}".format(tracking_num))
    
    # ── remove cookies ────────────────────────────────────────────────────
    _remove_cookies_popup(wds)

    # ── already delivered check ───────────────────────────────────────────
    check = Check(wds)
    if (check.already_delivered()):
        r.set_reason("Already delivered [DNR]")
        return r

    # ── click on notification button ──────────────────────────────────────
    notify_btn = wds.find.element(Locs.homepage["notify_me_btn"])
    if not (notify_btn):
        logger.debug("Failed to find notify button ({})".format(Locs.homepage["notify_me_btn"]))
        r.set_reason("Failed to find notify me button")
        return r
    wds.misc.scrollToElement(notify_btn, centered=True)
    sleep(1)
    wds.click.element(notify_btn)

    # ── get past first popup ──────────────────────────────────────────────
    popup   = wds.find.element(Locs.popup["container"])
    buttons = wds.find.buttons_within(popup, "continue")
    continue_button = buttons[0] if buttons else None
    if ( not continue_button ):
        logger.debug("Failed to find continue button. Locator: {}".format(Locs.popup["continue_button"]))
        r.set_reason("Failed to find continue button")
        return r
    wds.click.element(continue_button)

    # ── find available options and click them ─────────────────────────────
    elms_options = _get_options(wds)
    for elm in elms_options:
        wds.click.element(elm)

    # ── input emails ──────────────────────────────────────────────────────
    wds.input.by_locator(Locs.popup["email_input_1"], getenv("UPS_EMAIL1"))
    wds.input.by_locator(Locs.popup["email_input_2"], getenv("UPS_EMAIL2"))
    wds.click.by_locator(Locs.popup["done_btn"])

    # ── wait a bit then click close ───────────────────────────────────────
    sleep(1)
    wds.click.by_locator(Locs.popup["close_btn"])

    # ── return results ────────────────────────────────────────────────────
    r.set_result(Result.SUCCESS)
    return r
 



            

