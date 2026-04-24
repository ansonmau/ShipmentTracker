# Selenium imports
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Project imports
from core.driver.locator import Locator, ElementTypes

class Find:
    def __init__(self, wds):
        self.wds = wds
        self.driver = wds.driver

    def element(self, locator, wait=0):
        element = None

        if (not wait):
            wait = self.wds.default_wait_time

        try:
            element = WebDriverWait(self.driver, wait).until(
                EC.presence_of_element_located((locator.get_type(), locator.get_locator()))
            )
        except NoSuchElementException:
            element = None
        except TimeoutException:
            element = None

        return element

    def element_in_parent(self, parent_element, locator, wait=0):
        element = None
        if (not wait):
            wait = self.wds.default_wait_time

        if (parent_element != None):
            try:
                element = WebDriverWait(self.driver, wait).until(
                    lambda d: parent_element.find_element(locator.get_type(), locator.get_locator())
                )
            except NoSuchElementException:
                element = None
            except TimeoutException:
                element = None

        return element

    def all(self, locator, wait=0):
        elements = []
        if (not wait):
            wait = self.wds.default_wait_time

        try:
            elements = WebDriverWait(self.driver, wait).until(
                EC.presence_of_all_elements_located((locator.get_type(), locator.get_locator()))
            )
        except NoSuchElementException:
            elements = []
        except TimeoutException:
            elements = []

        return elements

    def all_in_parent(self, parent_element, locator, wait=0):
        elements = []
        if (not wait):
            wait = self.wds.default_wait_time

        if (parent_element != None):
            try:
                elements = WebDriverWait(self.driver, wait).until(
                    lambda d: parent_element.find_elements(locator.get_type(), locator.get_locator())
                )
            except NoSuchElementException:
                elements = []
            except TimeoutException:
                elements = []

        return elements

    def links_within(self, parent_element, filter='', wait=0):
        elements = []

        if (parent_element == None):
            return elements

        if (not wait):
            wait = self.wds.default_wait_time

        links = Locator(ElementTypes.tag, 'a')
        elements = self.all_in_parent(parent_element, links)

        if filter:
            elements = [el for el in elements if filter in self.wds.read.textFromElement(el)]

        return elements

    def buttons_within(self, parent_element, filter=None, wait=0) -> list:
        elements = []

        if (parent_element == None):
            return elements

        if (not wait):
            wait = self.wds.default_wait_time

        button_locator = Locator(ElementTypes.tag, 'button')
        elements = self.all_in_parent(parent_element, button_locator)

        if filter:
            elements = [el for el in elements if filter in self.wds.read.textFromElement(el)]

        return elements

    def inputs_within(self, parent_element, filter=None, wait=0):
        elements = []

        if (parent_element == None):
            return elements

        if (not wait):
            wait = self.wds.default_wait_time

        input_locator = Locator(ElementTypes.tag, 'input')
        elements = self.all_in_parent(parent_element, input_locator)

        if filter:
            elements = [el for el in elements if filter in self.wds.read.textFromElement(el)]

        return elements

    def select_list(self, locator):
        select_elm = self.wds.find.element(locator)

        return Select(select_elm)
