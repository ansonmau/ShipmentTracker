from core.driver.driver import WebDriverSession
from core.driver.locator import Locator, ElementTypes

from os import getenv
from core.settings import settings
from core.log import getLogger
from datetime import datetime, timedelta

logger = getLogger(__name__)

class Paths:
    startpage = {"login_btn": Locator(ElementTypes.css, ".menu-login")}

    login = {
        "user_input": Locator(ElementTypes.id, "j_username"),
        "pw_input": Locator(ElementTypes.id, "j_password"),
        "login_btn": Locator(ElementTypes.css, ".next-btn"),
    }

    homepage = {
        "nav_bar": Locator(ElementTypes.css, ".main-menu-items"),
        "filter_bar": Locator(ElementTypes.css, ".tab-radio-bar"),
        "tracking_dropdown": Locator(ElementTypes.id, "trackDropdown"),
    }

    popup = {"dialog": Locator(ElementTypes.css, ".modal-dialog")}

    tracking_page = {
        "shipment_table": Locator(ElementTypes.css, ".shipments-table"),
        "table_entry": Locator(ElementTypes.tag, "tr"),
        "table_data": Locator(ElementTypes.tag, "td"),
    }

    div = Locator(ElementTypes.tag, "div")
    img = Locator(ElementTypes.tag, "img")



tracking_table_index = {
    "tracking_num": 3,
    "date": 4,
    "status": 7,
    "carrier": 1,
}


def login(sesh: WebDriverSession, worker):
    sesh.nav.get("https://www.freightcom.com")
    sesh.click.by_locator(Paths.startpage["login_btn"])
    sesh.input.by_locator(Paths.login["user_input"], getenv("FREIGHTCOM_USER"))
    sesh.input.by_locator(Paths.login["pw_input"], getenv("FREIGHTCOM_PW"))

    worker.pause_signal.emit()
    worker.pause_event.wait()
    worker.pause_event.clear()


def scrape(sesh: WebDriverSession, worker):
    data = {
        "UPS": [],
        "Canpar": [],
        "Purolator": [],
        "Canada Post": [],
        "Fedex": [],
    }
        
    login(sesh, worker)

    sesh.click.by_locator(Paths.homepage["tracking_dropdown"])

    trackingpage_btn = get_trackingpage_btn(sesh)
    sesh.click.element(trackingpage_btn)

    discard_btn = get_popup_discard_btn(sesh)
    sesh.click.element(discard_btn)

    read_table_into_dict(sesh, data)
    return data


def get_trackingpage_btn(sesh: WebDriverSession):
    nav_bar = sesh.find.element(Paths.homepage["nav_bar"])
    dashboard_links = sesh.find.links_within(nav_bar, filter="Tracking Dashboard")
    assert len(dashboard_links) == 1
    return dashboard_links[0]


def get_popup_discard_btn(sesh: WebDriverSession):
    dialog = sesh.find.element(Paths.popup["dialog"])
    discard_btn = sesh.find.buttons_within(dialog, filter="Discard Progress")
    assert len(discard_btn) == 1
    return discard_btn[0]


def read_table_into_dict(sesh: WebDriverSession, info):
    carrier_name_converter = {
            "UPS": "UPS",
            "Canpar": "Canpar",
            "Purolator": "Purolator",
            "Canada Post": "Canada Post",
            "FedEx Courier": "Fedex",
        }

    table = sesh.find.element(Paths.tracking_page["shipment_table"])

    entries = sesh.find.all_in_parent(table, Paths.tracking_page["table_entry"])

    for entry in entries:
        if not check_valid_row(sesh, entry):
            continue

        data = sesh.find.all_in_parent(entry, Paths.tracking_page["table_data"])
        carrier, tracking_num, date, status = parse_entry_data(sesh, data)
        carrier = carrier_name_converter[carrier]

        logger.debug(f"Entry found: {carrier} | {tracking_num} | {date} | {status}")
        
        if not within_date_range(date):
            # break here since it's ordered by date.
            break 
        
        status = status.lower()
        if not "ready for shipping" in status and not "in transit" in status:
            logger.debug(f"entry {tracking_num} not ready for shipping / in transit")
            continue
        
        if not carrier in info:
            logger.warning(f"Carrier not found: {carrier}")

        info[carrier].append(tracking_num)



def parse_entry_data(sesh: WebDriverSession, row):
    carrier = get_carrier_name(sesh, row[tracking_table_index["carrier"]])

    tracking_num = sesh.read.element_text(row[tracking_table_index["tracking_num"]])
    # this text has 2 parts to it (tracking number and some other random text after a '\n')
    tracking_num = tracking_num.split("\n")[0]

    status = sesh.read.element_text(row[tracking_table_index["status"]])

    date = sesh.read.element_text(row[tracking_table_index["date"]])

    return carrier, tracking_num, date, status


def get_carrier_name(sesh: WebDriverSession, carrier_entry_elm):
    # first div child -> first img child -> "alt" attribute

    div_child = sesh.find.element_in_parent(carrier_entry_elm, Paths.div)
    img_child = sesh.find.element_in_parent(div_child, Paths.img)

    return sesh.read.element_attribute(img_child, "alt")

def check_valid_row(sesh: WebDriverSession, row):
    # website uses a new entry for putting in the "watched shipment" visual
    if "Watched Shipment" in sesh.read.element_text(row):
        return False
    return True

def within_date_range(date):
    site_date_format = "%b %d, %Y"
    check_date = datetime.strptime(date, site_date_format)
    lower_bound = datetime.now() - timedelta(days=settings['day_diff'])

    return check_date >= lower_bound
