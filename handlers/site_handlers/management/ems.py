from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from core.log import getLogger

logger = getLogger(__name__)

login_paths = {
        "login_menu_btn": (ELEMENT_TYPES['css'], '.app-login'),
        "login_options_menu": (ELEMENT_TYPES['css'], '.app-login__options__item'),
        "login_options": (ELEMENT_TYPES['tag'], 'a'),
        "username_input": (ELEMENT_TYPES['id'], 'username'),
        "password_input": (ELEMENT_TYPES['id'], 'password'),
        "login_btn": (ELEMENT_TYPES['css'], '[name="submit"]'),
}

def login(sesh: WebDriverSession):
        sesh.get("https://www.ems.post")
        sesh.click.path(login_paths['login_menu_btn'])

        options_menu = sesh.find.path(login_paths['login_options_menu'])
        login_btn, forgot_pw, request_acc = sesh.find.allFromParent(login_paths['login_options'], options_menu)
        sesh.click.element(login_btn)

        sesh.input.path(login_paths['username_input'], getenv("EMS_USER"))
        sesh.input.path(login_paths['password_input'], getenv("EMS_PW"))

        sesh.click.path(login_paths['login_btn'])

def scrape(sesh: WebDriverSession):
        pass

