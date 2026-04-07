from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.chrome.options import Options

import undetected_chromedriver as uc

from core.log import getLogger
from core.utils import PROJ_FOLDER

from core.driver.nav import Nav
from core.driver.find import Find
from core.driver.read import Read
from core.driver.filter import Filter
from core.driver.input import Input
from core.driver.misc import Misc
from core.driver.select import Select
from core.driver.tabs import TabControl
from core.driver.wait import Wait
from core.driver.click import Click

logger = getLogger(__name__)

class WebDriverSession:
    def __init__(self):
        self.driver = None
        self.default_wait_time = 10
        self.undetected = False 

        self.nav = Nav(self)
        self.find = Find(self)
        self.click = Click(self)
        self.wait = Wait(self)
        self.input = Input(self)
        self.filter = Filter(self)
        self.read = Read(self)
        self.tabControl = TabControl(self)
        self.select = Select(self)
        self.misc = Misc(self)
         
    def __del__(self):
        self.driver.quit()

    def is_alive(self):
        return (self.driver != None)

    def setUndetected(self, b):
        self.undetected = b

    def start(self):
        options = self._getOptions()

        try:
            if self.undetected:
                self.driver = uc.Chrome(options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
            self.driver.maximize_window()
        except SessionNotCreatedException as e:
            if e.msg:
                if "this version of chromedriver only supports" in e.msg.lower():
                    logger.critical("Chrome outdated. Please update.")
                else:
                    logger.critical("Unknwon webdriver error:\n{}".format(e.msg))
                return False

        return True

    def _getOptions(self):
        downloadPath = str((PROJ_FOLDER / 'data' / 'dls').resolve())

        # set options for downloading
        prefs = {
            "download.default_directory": downloadPath,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }

        options = uc.ChromeOptions() if self.undetected else Options()

        options.add_experimental_option("prefs", prefs)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        return options

