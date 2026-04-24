class Nav:
    def __init__(self, wds):
        self.wds = wds
        self.driver = wds.driver

    def get(self, url):
        self.driver.get(url)
