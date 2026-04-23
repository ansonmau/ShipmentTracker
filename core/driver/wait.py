from time import sleep
from time import time as now
from random import uniform
from selenium.webdriver.support.ui import WebDriverWait

class Wait:
    def __init__(self, wds):
        self.wds = wds
        self.driver = wds.driver

    def pageLoad(self, wait=0):
        if (not wait):
            wait = self.wds.default_wait_time

        WebDriverWait(self.driver, wait).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def element_located(self, locator, wait=0):
        if (not wait):
            wait = self.wds.default_wait_time

        end_time = now() + wait
        while (now() < end_time):
            if (self.wds.find.element(locator, wait=1)):
                return True
        return False
    
    def random(self, min=0.25, max=0.75):
        sleep(uniform(min, max))
