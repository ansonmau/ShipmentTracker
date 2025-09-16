from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv

class Paths:
        startpage = {
                "login_btn": (ELEMENT_TYPES['css'], '.menu-login')
        }

        login = {
                "user_input": (ELEMENT_TYPES['id'], 'j_username'),
                "pw_input": (ELEMENT_TYPES['id'], 'j_password'),
                "login_btn": (ELEMENT_TYPES['css'], '.next-btn'),
        }

        homepage = {
                "nav_bar": (ELEMENT_TYPES['css'], '.main-menu-items'),
                "filter_bar": (ELEMENT_TYPES['css'], '.tab-radio-bar'),
                "tracking_dropdown": (ELEMENT_TYPES['id'], 'trackDropdown'),
        }

        popup = {
                "dialog": (ELEMENT_TYPES['css'], '.modal-dialog')
        }



def login(sesh: WebDriverSession):
        sesh.get("https://www.freightcom.com")
        sesh.click.path(Paths.startpage['login_btn'])
        sesh.input.path(Paths.login['user_input'], getenv("FREIGHTCOM_USER"))
        sesh.input.path(Paths.login['pw_input'], getenv("FREIGHTCOM_PW"))
        
        input("[INPUT REQUIRED] Complete login process then come back and press enter")
        pass 

def test(sesh: WebDriverSession):
        login(sesh)

        sesh.click.path(Paths.homepage['tracking_dropdown'])
        
        trackingpage_btn = get_trackingpage_btn(sesh)
        sesh.click.element(trackingpage_btn)

        discard_btn = get_popup_discard_btn(sesh)
        sesh.click.element(discard_btn)

        pass

def get_trackingpage_btn(sesh: WebDriverSession):
        nav_bar = sesh.find.path(Paths.homepage['nav_bar'])
        dashboard_links = sesh.find.links_within(nav_bar, filter="Tracking Dashboard")
        assert len(dashboard_links) == 1
        return dashboard_links[0]

def get_popup_discard_btn(sesh: WebDriverSession):
        dialog = sesh.find.path(Paths.popup['dialog'])
        discard_btn = sesh.find.buttons_within(dialog, filter="Discard Progress")
        assert len(discard_btn) == 1
        return discard_btn[0]