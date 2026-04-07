from core.driver.driver import WebDriverSession

from selenium.common.exceptions import TimeoutException

class TabControl:
    def __init__(self, wds: WebDriverSession):
        self.wds = wds
        self.driver = wds.driver

    def _waitForNewTab(self, wait=0):
        if (not wait):
            wait = self.wds.default_wait_time

        curr_num_tabs = len(self.driver.window_handles)
        try:
            WebDriverWait(self.driver, wait).until(
                lambda x: len(x.window_handles) > curr_num_tabs
            )
            return True
        except TimeoutException:
            pass

        return False

    def getNumTabs(self):
        return len(self.getTabs())

    def getTabs(self):
        return self.driver.window_handles

    def getCurrentTab(self):
        return self.driver.current_window_handle

    def focusTab(self, tab):
        self.driver.switch_to.window(tab)

    def focusNewestTab(self):
        newest_tab = self.getTabs()[-1]
        self.focusTab(newest_tab)
