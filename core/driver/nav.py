from core.driver.driver import WebDriverSession

class Nav:
    def __init__(self, wds: WebDriverSession):
        self.wds = wds
        self.driver = wds.driver

    def get(self, url):
        self.driver.get(url)
