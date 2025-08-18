from driver import WebDriverSession, ELEMENT_TYPES
from os import getenv

paths = {
        "username_input": (ELEMENT_TYPES['id'], 'username'),
        "password_input": (ELEMENT_TYPES['id'], 'password'),
        "login_button": (ELEMENT_TYPES['css'], '[aria-label="Login Button"]'),
        "searchBox_input": (ELEMENT_TYPES['css'], 'placeholder="Search"'),
        "packages_table": (ELEMENT_TYPES['css'], '#cdk-drop-list-2 > tbody:nth-child(2)'),

}


def login(sesh: WebDriverSession):
        sesh.get("https://ww2.eshipper.com/login")

        sesh.inputText(paths['username_input'], getenv('ESHIPPER_USER'))
        sesh.inputText(paths['password_input'], getenv('ESHIPPER_PW'))
        sesh.click(paths['login_button'])

def scrape(sesh: WebDriverSession):
        sesh.get("https://ww2.eshipper.com/customer/tracking")


        pTable = sesh.find(paths['packages_table'])
        
