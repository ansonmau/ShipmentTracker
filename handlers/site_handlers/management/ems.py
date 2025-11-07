from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from core.log import getLogger
from time import sleep
from main import DAY_DIFF

from datetime import datetime, timedelta

logger = getLogger(__name__)

class Paths:
    login = {
            "username": (ELEMENT_TYPES['id'], 'email'),
            "password": (ELEMENT_TYPES['css'], '[name="password"]'),
            "login_btn": (ELEMENT_TYPES['id'], 'doSubmit'),
            }

    shipment_page = {
            "shipment_table": (ELEMENT_TYPES['id'], 'shipmentTable'),
            "date_filter_div": (ELEMENT_TYPES['css'], '.input-daterange'),
            "filter_search": (ELEMENT_TYPES['id'], 'm_search'),
            "table_length_selector": (ELEMENT_TYPES['css'], '[name="shipmentTable_length"]'),
            "table_next_btn": (ELEMENT_TYPES['id'], 'shipmentTable_next')
            }


def scrape(sesh: WebDriverSession):
    data = {
        "UPS": [],
        "Canpar": [],
        "Purolator": [],
        "Canada Post": [],
        "Fedex": [],
    }
    
    login(sesh)

    shipment_page_url = "https://emarketplaceservices.com/shipments"
    sesh.get(shipment_page_url)

    s_from_date, s_today = get_filter_dates(DAY_DIFF)
    from_date_input, to_date_input = get_filter_inputs(sesh)

    sesh.input.element(from_date_input, s_from_date)
    sesh.input.element(to_date_input, s_today)
    sesh.click.path(Paths.shipment_page['filter_search'])

    table_length_selector = sesh.find.select_list(Paths.shipment_page['table_length_selector'])
    sesh.select.by_value(table_length_selector, '100')

    logger.info("Waiting for table to update...")    
    sleep(3) # takes a second to update    
    logger.info("Reading table...")

    next_page = True
    while next_page:
        table_entries = get_shipment_table_entries(sesh)
        for entry in table_entries:
            carrier, tracking_num, status = parse_table_entry(sesh, entry)
            logger.debug(f"Entry found: {carrier} | {tracking_num} | {status}")
            if carrier and tracking_num and status:
                data[carrier].append(tracking_num)

        next_page = go_next_shipment_page(sesh)

    return data

def login(sesh: WebDriverSession):
    login_url = "https://emarketplaceservices.com/login"
    sesh.get(login_url)
    
    sesh.input.path(Paths.login["username"], getenv("EMS_USER"))
    sesh.input.path(Paths.login["password"], getenv("EMS_PW"))

    sesh.click.path(Paths.login["login_btn"])
    
def get_filter_dates(day_diff=3):
    date_format = "%m/%d/%Y"
    s_today = datetime.now().strftime(date_format)
    
    from_date = datetime.now() - timedelta(days=day_diff)
    s_from_date = from_date.strftime(date_format)

    return s_from_date, s_today

def get_filter_inputs(sesh: WebDriverSession):
    filter_div = sesh.find.path(Paths.shipment_page['date_filter_div'])
    
    # find inputs within filter_div -> return individually
    inputs = sesh.find.inputs_within(filter_div)
    
    assert len(inputs) == 2
    return inputs[0], inputs[1]

def get_shipment_table_entries(sesh: WebDriverSession):
    table_entry_loc = (ELEMENT_TYPES['tag'], 'tr')

    table_elm = sesh.find.path(Paths.shipment_page['shipment_table'])
    table_entries = sesh.find.allFromParent(table_elm, table_entry_loc)

    return table_entries

def parse_table_entry(sesh: WebDriverSession, entry_elm):
    index = {
            "tracking_number": 5,
            "status": 8,
            }

    tracking_num = ''
    carrier = ''
    status = ''

    entry_part_loc = (ELEMENT_TYPES['tag'], 'td')
    entry_parts = sesh.find.allFromParent(entry_elm, entry_part_loc)

    if entry_parts:
        tracking_num = sesh.read.textFromElement(entry_parts[index['tracking_number']])
        # get text up until first \n (rest is customer info)
        tracking_num = tracking_num.split('\n')[0]
        
        carrier = _get_carrier(sesh, entry_parts[index['tracking_number']])

        status = sesh.read.textFromElement(entry_parts[index['status']])

    return carrier, tracking_num, status

def go_next_shipment_page(sesh:WebDriverSession) -> bool:
    next_btn = sesh.find.path(Paths.shipment_page['table_next_btn'])
    
    if 'disabled' in sesh.read.attributeFromElement(next_btn, 'class'):
        return False
    
    sesh.click.element(next_btn)
    sleep(3)
    return True

def _get_carrier(sesh: WebDriverSession, entry_part):
        carriers = {
            'purolator':'Purolator',
            'ups':'UPS',
            'canadapost':'Canada Post',
            'fedex':'Fedex',
            'canpar':'Canpar',
        }

        carrier_link_elm = sesh.find.links_within(entry_part)[0]
        carrier_link = sesh.read.attributeFromElement(carrier_link_elm, 'href')
        for c in carriers:
            if c in carrier_link:
                return carriers[c]

