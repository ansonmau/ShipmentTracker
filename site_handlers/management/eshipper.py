from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from core.log import getLogger

logger = getLogger()

paths = {
        "username_input": (ELEMENT_TYPES['id'], 'username'),
        "password_input": (ELEMENT_TYPES['id'], 'password'),
        "login_button": (ELEMENT_TYPES['css'], '[aria-label="Login Button"]'),
        "usernameText": (ELEMENT_TYPES['css'], '.userNameText'),
        "options_button": (ELEMENT_TYPES['css'], '.dot-menu'),
        "options_menu_buttons": (ELEMENT_TYPES['css'], '.men-item-btn'),
        "export_options_container": (ELEMENT_TYPES['css'], '.file-cards'),
        "export_options": (ELEMENT_TYPES['tag'], 'li'),
        "export_button": (ELEMENT_TYPES['css'], '[aria-label="Export Track Button"]'),
}


def login(sesh: WebDriverSession):
        sesh.get("https://ww2.eshipper.com/login")

        sesh.input.path(paths['username_input'], getenv('ESHIPPER_USER'))
        sesh.input.path(paths['password_input'], getenv('ESHIPPER_PW'))

        sesh.click.path(paths['login_button'])

        sesh.waitFor.path(paths['usernameText'])

def scrape(sesh: WebDriverSession):
        login(sesh)

        sesh.get("https://ww2.eshipper.com/customer/tracking")

        sesh.click.path(paths['options_button'])
        
        # can't find export button explicitly (consistently), so just going with second options menu item (1 - print, 2 - export)
        menu_btns = sesh.find.all(paths['options_menu_buttons'])
        _, export_btn = menu_btns

        sesh.click.element(export_btn)

        # can't find the csv option explicitly (consistently), so just going with first link (1 - csv, 2 - xl)
        export_options_container = sesh.find.path(paths['export_options_container'])
        export_options = sesh.find.allFromParent(export_options_container, paths['export_options'])

        export_as_csv,_ = export_options
        sesh.click.element(export_as_csv)

        sesh.click.path(paths['export_button'])

        


