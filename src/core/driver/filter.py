from core.driver.locator import Locator, ElementTypes

class Filter:
    def __init__(self, wds):
        self.wds = wds
        self.driver = wds.driver

    def by_text(self, element_list, txt):
        elmnts = []
        for elmnt in element_list:
            if self.wds.read.element_text(elmnt) == txt:
                elmnts.append(elmnt)
        return elmnts

    def by_attribute(self, elm_list, attribute, search_val):
        elmnts = []
        search_val = search_val.lower()

        for elmnt in elm_list:
            attr_text = elmnt.get_attribute(attribute).lower()
            if search_val in attr_text:
                elmnts.append(elmnt)

        return elmnts
