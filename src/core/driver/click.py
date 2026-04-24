from core.driver.locator import Locator, ElementTypes

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


    def by_locator(self, locator):
        element = self.wds.find.element(locator)
        self._click_element(element)

