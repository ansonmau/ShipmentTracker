from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from core.log import getLogger

logger = getLogger(__name__)

class Paths:
    homepage = {
            "login_btn": (ELEMENT_TYPES['css'], '.app-login')
            }

    login = {
            "username": (ELEMENT_TYPES['id'], 'username'),
            "password": (ELEMENT_TYPES['id'], 'password'),
            "login_btn": (ELEMENT_TYPES['css'], '[name="submit"]'),
            }


def scrape(sesh: WebDriverSession):
    login(sesh)

    return

def login(sesh: WebDriverSession):
    login_url = "https://www.ems.post/en/global-network/tracking"
    
    sesh.get(login_url)
    login_btn_elm = sesh.find.path(Paths.homepage["login_btn"])
    sesh.click.element(login_btn_elm)
    
    login_btn_2_elm = sesh.find.links_within(login_btn_elm, filter="Login")[0]
    sesh.click.element(login_btn_2_elm)

    sesh.input.path(Paths.login["username"], getenv("EMS_USER"))
    sesh.input.path(Paths.login["password"], getenv("EMS_PW"))

    sesh.click.path(Paths.login["login_btn"])
    
