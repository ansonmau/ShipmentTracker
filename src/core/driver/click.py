from selenium.common.exceptions import ElementClickInterceptedException
from src.core.driver.locator import Locator, ElementTypes
import src.core.utils as utils

class Click:
    def __init__(self, wds):
        self.wds = wds

    def _click_element(self, target_element):
        if (target_element):
            target_element.click()
            self.wds.wait.random()

    def element(self, elmnt):
        self._click_element(elmnt)

    def element_in_parent(self, parent_element, locator):
        element = self.wds.find.element_in_parent(parent_element, locator)
        self._click_element(element)

    def element_through_intercept(self, element, time=5):
        t = utils.Timer()
        t.start(time)
        while (t.check()):
            try:
                self.wds.click.element(element)
                return 0
            except ElementClickInterceptedException:
                pass
        return 1


    def by_locator(self, locator):
        element = self.wds.find.element(locator)
        self._click_element(element)

