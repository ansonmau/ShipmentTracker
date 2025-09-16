from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv

class Paths:
        homepage = {
                "login_btn": (ELEMENT_TYPES['css'], '.menu-login')
        }

        login = {
                "user_input": (ELEMENT_TYPES['id'], 'j_username'),
                "pw_input": (ELEMENT_TYPES['id'], 'j_password'),
                "login_btn": (ELEMENT_TYPES['css'], '.next-btn'),
        }

def login(sesh: WebDriverSession):
        sesh.get("https://www.freightcom.com")
        sesh.click.path(Paths.homepage['login_btn'])
        sesh.input.path(Paths.login['user_input'], getenv("FREIGHTCOM_USER"))
        sesh.input.path(Paths.login['pw_input'], getenv("FREIGHTCOM_PW"))
        
        input("[INPUT REQUIRED] Complete login process then come back and press enter")
        pass 

def test(sesh:WebDriverSession):
        login(sesh)
        