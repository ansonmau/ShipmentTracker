class Input:
    def __init__(self, wds):
        self.wds = wds

    def _sendKeys(self, target_element, keys):
        if (target_element):
            self.wds.click.element(target_element)
            for key in keys:
                target_element.send_keys(key)
                self.wds.wait.random(0.09, 0.15) # based on 100WPM 5 letter words on average (60 / 100*5 = 0.12 average) delta = 0.3

    def element(self, element, txt):
        self._sendKeys(element, txt)

    def by_locator(self, locator, txt):
        element = self.wds.find.element(locator)

        if (element):
            self._sendKeys(element, txt)
