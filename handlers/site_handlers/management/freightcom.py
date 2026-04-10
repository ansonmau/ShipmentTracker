from core.driver.locator import Locator, ElementTypes

from os import getenv
from core.settings import Settings
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

def login(wds, worker):
    wds.nav.get("https://www.freightcom.com")
    wds.click.by_locator(Paths.startpage["login_btn"])
    wds.input.by_locator(Paths.login["user_input"], getenv("FREIGHTCOM_USER"))
    wds.input.by_locator(Paths.login["pw_input"], getenv("FREIGHTCOM_PW"))

    worker.pause_signal.emit()
    worker.pause_event.wait()
    worker.pause_event.clear()


def scrape(wds, worker):
    data = {
        "UPS": [],
        "Canpar": [],
        "Purolator": [],
        "Canada Post": [],
        "Fedex": [],
    }
        
    login(wds, worker)

    wds.click.by_locator(Paths.homepage["tracking_dropdown"])
    trackingpage_btn = get_trackingpage_btn(wds)
    wds.click.element(trackingpage_btn)

    discard_btn = get_popup_discard_btn(wds)
    wds.click.element(discard_btn)

    table = TableHandler(wds, output_dict = data)
    table.parse_table_to_dict()
    return data


def get_trackingpage_btn(wds):
    nav_bar = wds.find.element(Paths.homepage["nav_bar"])
    dashboard_links = wds.find.links_within(nav_bar, filter="Tracking Dashboard")[0]
    return dashboard_links


def get_popup_discard_btn(wds):
    dialog = wds.find.element(Paths.popup["dialog"])
    discard_btn = wds.find.buttons_within(dialog, filter="Discard Progress")
    assert len(discard_btn) == 1
    return discard_btn[0]

def within_date_range(date):
    site_date_format = "%b %d, %Y"
    check_date = datetime.strptime(date, site_date_format)
    lower_bound = datetime.now() - timedelta(days=Settings.get_settings()['day_diff'])

    return check_date >= lower_bound

class TableHandler:
    carrier_name_converter = {
            "UPS": "UPS",
            "Canpar": "Canpar",
            "Purolator": "Purolator",
            "Canada Post": "Canada Post",
            "FedEx Courier": "Fedex",
        }

    tracking_table_index = {
        "carrier": 1,
        "tracking_num": 3,
        "date": 4,
        "status": 7,
    }

    def __init__(self, wds, output_dict):
        self.wds = wds
        self.driver = wds.driver
        self.output_dict = output_dict

    def parse_table_to_dict(self):
        table = self.wds.find.element(Paths.tracking_page["shipment_table"])
        entries = self.wds.find.all_in_parent(table, Paths.tracking_page["table_entry"])

        for row in entries:
            if not self._is_valid_row(row):
                continue

            carrier, tracking_num, date, status = self._parse_row(row)

            if not within_date_range(date):
                # break here since it's ordered by date.
                break 

            status = status.lower()
            if ((not "ready for shipping" in status) and (not "in transit" in status)):
                logger.debug(f"entry {tracking_num} not ready for shipping / in transit")
                continue

            logger.debug(f"Entry found: {carrier} | {tracking_num} | {date} | {status}")
            
            if (carrier not in self.output_dict):
                logger.error("Failed to find matching carrier name for '{}'".format(carrier))

            self.output_dict[carrier].append(tracking_num)
    
    def _is_valid_row(self, row_element):
        if "Watched Shipment" in self.wds.read.element_text(row_element):
            return False
        return True
    
    def _parse_row(self, row_element):
        data = self.wds.find.all_in_parent(row_element, Paths.tracking_page["table_data"])
        carrier = self.__get_carrier_name_from_element(data[self.tracking_table_index["carrier"]])

        tracking_num = self.wds.read.element_text(data[self.tracking_table_index["tracking_num"]])
        # this text has 2 parts to it (tracking number and some other random text after a '\n')
        tracking_num = tracking_num.split("\n")[0]

        status = self.wds.read.element_text(data[self.tracking_table_index["status"]])
        date = self.wds.read.element_text(data[self.tracking_table_index["date"]])

        return carrier, tracking_num, date, status

    def __get_carrier_name_from_element(self, carrier_element):
        div_child = self.wds.find.element_in_parent(carrier_element, Paths.div)
        img_child = self.wds.find.element_in_parent(div_child, Paths.img)

        carrier_name = self.wds.read.element_attribute(img_child, "alt")

        if (carrier_name not in self.carrier_name_converter):
            logger.warning(f"Carrier not found: {carrier_name}")
            return ""

        return self.carrier_name_converter[carrier_name]
