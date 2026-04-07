from core.driver.driver import WebDriverSession
from core.driver.locator import Locator, ElementTypes

class Click:
    def __init__(self, wds: WebDriverSession):
        self.wds = wds

    def _click_element(self, target_element):
        if (target_element):
            target_element.click()
            self.wds.wait.random()

    def element(self, elmnt):
        self._click_element(elmnt)

    def by_locator(self, locator):
        element = self.wds.find.path(locator)
        self._click_element(element)

