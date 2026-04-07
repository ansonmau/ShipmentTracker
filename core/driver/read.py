from core.driver.driver import WebDriverSession

class Read:
    def __init__(self, wds: WebDriverSession):
        self.wds = wds

    def text(self, locator):
        return self.element_text(self.wds.find.element(locator))

    def attribute(self, locator, attr_name):
        elm = self.wds.find.element(locator)
        return self._get_element_attribute(elm, attr_name)

    def element_text(self, element):
        return self._get_element_text(element)

    def element_attribute(self, elm, attr_name):
        return self._get_element_attribute(elm, attr_name)

    def _get_element_attribute(self, element, attribute):
        if element:
            return element.get_attribute(attribute)

    def _get_element_text(self, element):
        if element:
            return element.text


