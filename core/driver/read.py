class Read:
    def __init__(self, wds):
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
        attribute = element.get_attribute(attribute) if element else ''
        return attribute

    def _get_element_text(self, element):
        text = element.text if element else ''
        return text


