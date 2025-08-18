from driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from log import getLogger

logger = getLogger()

paths = {
        "username_input": (ELEMENT_TYPES['id'], 'username'),
        "password_input": (ELEMENT_TYPES['id'], 'password'),
        "login_button": (ELEMENT_TYPES['css'], '[aria-label="Login Button"]'),
        "searchBox_input": (ELEMENT_TYPES['css'], 'placeholder="Search"'),
        "packages_table": (ELEMENT_TYPES['css'], '#cdk-drop-list-2 > tbody:nth-child(2)'),
        "entries_fromPackagesTable": (ELEMENT_TYPES['css'], 'tr'),
        "packageNumber_fromEntries": (ELEMENT_TYPES['css'], '[class="link-text"]'),
        "usernameText": (ELEMENT_TYPES['css'], '.userNameText')
}


def login(sesh: WebDriverSession):
        sesh.get("https://ww2.eshipper.com/login")

        sesh.inputText(paths['username_input'], getenv('ESHIPPER_USER'))
        sesh.inputText(paths['password_input'], getenv('ESHIPPER_PW'))
        sesh.click(paths['login_button'])

        sesh.waitFor(paths['usernameText'])

def scrape(sesh: WebDriverSession):
        sesh.get("https://ww2.eshipper.com/customer/tracking")

        pTable = sesh.find(paths['packages_table'])
        pTable_entries = sesh.findAllFromParent(pTable, paths['entries_fromPackagesTable'])

        for entry in pTable_entries:
                element = sesh.findFromParent(entry, paths['packageNumber_fromEntries'])
                pass
        


