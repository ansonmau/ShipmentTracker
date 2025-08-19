from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from core.log import getLogger


logger = getLogger()

paths = {
        "username_input": (ELEMENT_TYPES['id'], 'username'),
        "password_input": (ELEMENT_TYPES['id'], 'password'),
        "login_button": (ELEMENT_TYPES['css'], '[aria-label="Login Button"]'),
        "usernameText": (ELEMENT_TYPES['css'], '.userNameText'),
        "searchBox": {
                "parent": (ELEMENT_TYPES['css'], '.tracking-search'),
                "input": (ELEMENT_TYPES['css'], '.input-style'),
        },
        "packages_table": {
                "table": (ELEMENT_TYPES['css'], '.cdk-drop-list'),
                "cells": (ELEMENT_TYPES['tag'], 'tr'),
                "deliveryNum": (ELEMENT_TYPES['css'], 'b.link-text'),
        },
}


def login(sesh: WebDriverSession):
        sesh.get("https://ww2.eshipper.com/login")

        sesh.inputText(paths['username_input'], getenv('ESHIPPER_USER'))
        sesh.inputText(paths['password_input'], getenv('ESHIPPER_PW'))
        sesh.click(paths['login_button'])

        sesh.waitFor(paths['usernameText'])

def scrape(sesh: WebDriverSession):
        sesh.get("https://ww2.eshipper.com/customer/tracking")

        searchBox_parent = sesh.find(paths['searchBox']['parent'])
        searchBox = sesh.findFromParent(searchBox_parent, paths['searchBox']['input'])
        sesh.element_inputText(searchBox, "in transit")

        pTable = sesh.find(paths['packages_table']['table'])
        pTable_rows = sesh.findAllFromParent(pTable, paths['packages_table']['cells'])

        # first row is the table headers, skip em
        pTable_rows = pTable_rows[1:]

        for currRow in pTable_rows:
                element = sesh.findFromParent(currRow, paths['packages_table']['deliveryNum'])
                print(element.text)
                pass
        


