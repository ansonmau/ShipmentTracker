from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from core.log import getLogger

logger = getLogger(__name__)

class Paths:
    startpage = {"login_btn": (ELEMENT_TYPES["css"], ".menu-login")}

    login = {
        "user_input": (ELEMENT_TYPES["id"], "j_username"),
        "pw_input": (ELEMENT_TYPES["id"], "j_password"),
        "login_btn": (ELEMENT_TYPES["css"], ".next-btn"),
    }

    homepage = {
        "nav_bar": (ELEMENT_TYPES["css"], ".main-menu-items"),
        "filter_bar": (ELEMENT_TYPES["css"], ".tab-radio-bar"),
        "tracking_dropdown": (ELEMENT_TYPES["id"], "trackDropdown"),
    }

    popup = {"dialog": (ELEMENT_TYPES["css"], ".modal-dialog")}

    tracking_page = {
        "shipment_table": (ELEMENT_TYPES["css"], ".shipments-table"),
        "table_entry": (ELEMENT_TYPES["tag"], "tr"),
        "table_data": (ELEMENT_TYPES["tag"], "td"),
    }

    div = (ELEMENT_TYPES["tag"], "div")
    img = (ELEMENT_TYPES["tag"], "img")


tracking_table_index = {
    "tracking_num": 3,
    "status": 7,
    "carrier": 1,
}


def login(sesh: WebDriverSession):
    sesh.get("https://www.freightcom.com")
    sesh.click.path(Paths.startpage["login_btn"])
    sesh.input.path(Paths.login["user_input"], getenv("FREIGHTCOM_USER"))
    sesh.input.path(Paths.login["pw_input"], getenv("FREIGHTCOM_PW"))

    input("[INPUT REQUIRED] Complete login process then come back and press enter")


def scrape(sesh: WebDriverSession):
    data = {
        "UPS": [],
        "Canpar": [],
        "Purolator": [],
        "Canada Post": [],
        "Federal Express": [],
    }
        
    login(sesh)

    sesh.click.path(Paths.homepage["tracking_dropdown"])

    trackingpage_btn = get_trackingpage_btn(sesh)
    sesh.click.element(trackingpage_btn)

    discard_btn = get_popup_discard_btn(sesh)
    sesh.click.element(discard_btn)

    get_shipment_info(sesh, data)
    return data


def get_trackingpage_btn(sesh: WebDriverSession):
    nav_bar = sesh.find.path(Paths.homepage["nav_bar"])
    dashboard_links = sesh.find.links_within(nav_bar, filter="Tracking Dashboard")
    assert len(dashboard_links) == 1
    return dashboard_links[0]


def get_popup_discard_btn(sesh: WebDriverSession):
    dialog = sesh.find.path(Paths.popup["dialog"])
    discard_btn = sesh.find.buttons_within(dialog, filter="Discard Progress")
    assert len(discard_btn) == 1
    return discard_btn[0]


def get_shipment_info(sesh: WebDriverSession, info):
    table = sesh.find.path(Paths.tracking_page["shipment_table"])

    entries = sesh.find.allFromParent(table, Paths.tracking_page["table_entry"])

    for entry in entries:
        if not check_valid_row(sesh, entry):
            continue

        data = sesh.find.allFromParent(entry, Paths.tracking_page["table_data"])
        carrier, tracking_num, status = parse_entry_data(sesh, data)

        status = status.lower()
        if not "ready for shipping" in status and not "in transit" in status:
            continue
        
        if not carrier in info:
            logger.
        info[carrier].append(tracking_num)



def parse_entry_data(sesh: WebDriverSession, row):
    carrier = get_carrier_name(sesh, row[tracking_table_index["carrier"]])

    tracking_num = sesh.read.textFromElement(row[tracking_table_index["tracking_num"]])
    # this text has 2 parts to it (tracking number and some other random text after a '\n')
    tracking_num = tracking_num.split("\n")[0]

    status = sesh.read.textFromElement(row[tracking_table_index["status"]])

    return carrier, tracking_num, status


def get_carrier_name(sesh: WebDriverSession, carrier_entry_elm):
    # first div child -> first img child -> "alt" attribute

    div_child = sesh.find.fromParent(carrier_entry_elm, Paths.div)
    img_child = sesh.find.fromParent(div_child, Paths.img)

    return sesh.read.attributeFromElement(img_child, "alt")

def check_valid_row(sesh: WebDriverSession, row):
    # website uses a new entry for putting in the "watched shipment" visual
    if "Watched Shipment" in sesh.read.textFromElement(row):
        return False
    return True
