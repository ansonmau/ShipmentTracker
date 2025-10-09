from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from core.log import getLogger

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
            }


def scrape(sesh: WebDriverSession):
    login(sesh)
    
    shipment_page_url = "https://emarketplaceservices.com/shipments"
    sesh.get(shipment_page_url)

    s_from_date, s_today = get_filter_dates()
    from_date_input, to_date_input = get_filter_inputs(sesh)
    sesh.input.element(from_date_input, s_from_date)
    sesh.input.element(to_date_input, s_today)
    sesh.click.path(Paths.shipment_page['filter_search'])

    return

def login(sesh: WebDriverSession):
    login_url = "https://emarketplaceservices.com/login"
    sesh.get(login_url)
    
    sesh.input.path(Paths.login["username"], getenv("EMS_USER"))
    sesh.input.path(Paths.login["password"], getenv("EMS_PW"))

    sesh.click.path(Paths.login["login_btn"])
    
def get_filter_dates():
    date_format = "%m/%d/%Y"
    s_today = datetime.now().strftime(date_format)
    
    from_date = datetime.now() - timedelta(days=3)
    s_from_date = from_date.strftime(date_format)

    return s_from_date, s_today

def get_filter_inputs(sesh: WebDriverSession):
    filter_div = sesh.find.path(Paths.shipment_page['date_filter_div'])
    
    # find inputs within filter_div -> return individually
    inputs = sesh.find.inputs_within(filter_div)
    
    assert len(inputs) == 2
    return inputs[0], inputs[1]
