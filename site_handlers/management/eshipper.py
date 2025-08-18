from driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from log import getLogger

logger = getLogger()

paths = {
        "username_input": (ELEMENT_TYPES['id'], 'username'),
        "password_input": (ELEMENT_TYPES['id'], 'password'),
        "login_button": (ELEMENT_TYPES['css'], '[aria-label="Login Button"]'),
        "usernameText": (ELEMENT_TYPES['css'], '.userNameText'),
        "searchBox_input": (ELEMENT_TYPES['css'], '.ng-dirty'),
        "packages_table": (ELEMENT_TYPES['css'], '.cdk-drop-list'),
        "entries_fromPackagesTable": (ELEMENT_TYPES['tag'], 'tr'),
        "packageNumber_fromEntry": (ELEMENT_TYPES['css'], '.link-text'),
}


def login(sesh: WebDriverSession):
        sesh.get("https://ww2.eshipper.com/login")

        sesh.inputText(paths['username_input'], getenv('ESHIPPER_USER'))
        sesh.inputText(paths['password_input'], getenv('ESHIPPER_PW'))
        sesh.click(paths['login_button'])

        sesh.waitFor(paths['usernameText'])

def scrape(sesh: WebDriverSession):
        sesh.get("https://ww2.eshipper.com/customer/tracking")

        sesh.inputText(paths['searchBox_input'], "in transit")

        pTable = sesh.find(paths['packages_table'])
        pTable_entries = sesh.findAllFromParent(pTable, paths['entries_fromPackagesTable'])

        for entry in pTable_entries:
                element = sesh.findFromParent(entry, paths['packageNumber_fromEntry'])
                pass
        


