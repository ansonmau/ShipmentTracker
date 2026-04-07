class Input:
    def __init__(self, wds: WebDriverSession):
        self.wds = wds

    def _sendKeys(self, target_element, keys):
        if (target_element):
            self.wds.click.element(target_element)
            for key in keys:
                target_element.send_keys(key)
                self.wds.wait.random()

    def element(self, element, txt):
        self._sendKeys(element, txt)

    def by_locator(self, locator, txt):
        element = self.wds.find.element(locator)

        if (element):
            self._sendKeys(element, txt)
