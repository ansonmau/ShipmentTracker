from core.driver.driver import WebDriverSession
from core.driver.locator import Locator, ElementTypes
import core.settings as settings
from core.log import getLogger

from os import getenv
from time import sleep
from datetime import datetime, timedelta

logger = getLogger(__name__)

class Paths:
    login = {
            "username": Locator(ElementTypes.id, 'email'),
            "password": Locator(ElementTypes.css, '[name="password"]'),
            "login_btn": Locator(ElementTypes.id, 'doSubmit'),
            }

    shipment_page = {
            "shipment_table": Locator(ElementTypes.id, 'shipmentTable'),
            "date_filter_div": Locator(ElementTypes.css, '.input-daterange'),
            "filter_search": Locator(ElementTypes.id, 'm_search'),
            "table_length_selector": Locator(ElementTypes.css, '[name="shipmentTable_length"]'),
            "table_next_btn": Locator(ElementTypes.id, 'shipmentTable_next')
            }


def scrape(wds: WebDriverSession):
    data = {
        "UPS": [],
        "Canpar": [],
        "Purolator": [],
        "Canada Post": [],
        "Fedex": [],
    }
    
    if (not login(wds)):
        logger.error("Failed to log in to EMS")
        return data;

    wds.nav.get("https://emarketplaceservices.com/shipments")

    s_from_date, s_today = get_filter_dates(settings.settings["day_diff"])
    from_date_input, to_date_input = get_filter_inputs(wds)

    wds.input.element(from_date_input, s_from_date)
    wds.input.element(to_date_input, s_today)
    wds.click.by_locator(Paths.shipment_page['filter_search'])

    table_length_selector = wds.find.select_list(Paths.shipment_page['table_length_selector'])
    wds.select.by_value(table_length_selector, '100')

    logger.info("Waiting for table to update...")    
    sleep(5) # takes a second to update    
    logger.info("Reading table...")

    next_page = True
    while next_page:
        table_entries = get_shipment_table_entries(wds)
        for entry in table_entries:
            carrier, tracking_num, status = parse_table_entry(wds, entry)
            logger.debug(f"Entry found: {carrier} | {tracking_num} | {status}")
            if carrier and tracking_num and status:
                data[carrier].append(tracking_num)

        next_page = go_next_shipment_page(wds)

    return data

def login(wds: WebDriverSession):
    login_url = "https://emarketplaceservices.com/login"
    wds.nav.get(login_url)

    username_field = wds.find.element(Paths.login["username"])
    password_field = wds.find.element(Paths.login["password"])
    login_btn = wds.find.element(Paths.login["login_btn"])

    if ((not username_field) or (not password_field)):
        return 0
    
    wds.input.element(username_field, getenv("EMS_USER"))
    wds.input.element(password_field, getenv("EMS_PW"))
    wds.click.element(login_btn)
    return 1
    
def get_filter_dates(day_diff=3):
    date_format = "%m/%d/%Y"
    s_today = datetime.now().strftime(date_format)
    
    from_date = datetime.now() - timedelta(days=day_diff)
    s_from_date = from_date.strftime(date_format)

    return s_from_date, s_today

def get_filter_inputs(wds: WebDriverSession):
    filter_div = wds.find.element(Paths.shipment_page['date_filter_div'])
    
    # find inputs within filter_div -> return individually
    inputs = wds.find.inputs_within(filter_div)
    
    assert len(inputs) == 2
    return inputs[0], inputs[1]

def get_shipment_table_entries(wds: WebDriverSession):
    table_entry_loc = (ElementTypes.tag, 'tr')

    table_elm = wds.find.element(Paths.shipment_page['shipment_table'])
    table_entries = wds.find.all_in_parent(table_elm, table_entry_loc)

    return table_entries

def parse_table_entry(wds: WebDriverSession, entry_elm):
    index = {
            "tracking_number": 5,
            "status": 8,
            }

    tracking_num = ''
    carrier = ''
    status = ''

    entry_part_loc = (ElementTypes.tag, 'td')
    entry_parts = wds.find.all_in_parent(entry_elm, entry_part_loc)

    if entry_parts:
        tracking_num = wds.read.element_text(entry_parts[index['tracking_number']])
        # get text up until first \n (rest is customer info)
        tracking_num = tracking_num.split('\n')[0]
        
        carrier = _get_carrier(wds, entry_parts[index['tracking_number']])

        status = wds.read.element_text(entry_parts[index['status']])

    return carrier, tracking_num, status

def go_next_shipment_page(wds:WebDriverSession) -> bool:
    next_btn = wds.find.element(Paths.shipment_page['table_next_btn'])
    
    if 'disabled' in wds.read.element_attribute(next_btn, 'class'):
        return False
    
    wds.click.element(next_btn)
    sleep(3)
    return True

def _get_carrier(wds: WebDriverSession, entry_part):
        carriers = {
            'purolator':'Purolator',
            'ups':'UPS',
            'canadapost':'Canada Post',
            'fedex':'Fedex',
            'canpar':'Canpar',
        }

        carrier_link_elm = wds.find.links_within(entry_part)[0]
        carrier_link = wds.read.element_attribute(carrier_link_elm, 'href')
        for c in carriers:
            if c in carrier_link:
                return carriers[c]

