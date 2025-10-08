from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from core.log import getLogger

logger = getLogger(__name__)

class Paths:
    login = {
            "username": (ELEMENT_TYPES['id'], 'email'),
            "password": (ELEMENT_TYPES['css'], '[name="password"]'),
            "login_btn": (ELEMENT_TYPES['id'], 'doSubmit'),
            }


def scrape(sesh: WebDriverSession):
    login(sesh)

    return

def login(sesh: WebDriverSession):
    login_url = "https://emarketplaceservices.com/login"
    sesh.get(login_url)
    
    sesh.input.path(Paths.login["username"], getenv("EMS_USER"))
    sesh.input.path(Paths.login["password"], getenv("EMS_PW"))

    sesh.click.path(Paths.login["login_btn"])
    
