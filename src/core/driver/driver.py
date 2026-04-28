import re
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.chrome.options import Options

import undetected_chromedriver as uc

from src.core.log import getLogger
from src.core.utils import ROOT

from src.core.driver.nav import Nav
from src.core.driver.find import Find
from src.core.driver.read import Read
from src.core.driver.filter import Filter
from src.core.driver.input import Input
from src.core.driver.misc import Misc
from src.core.driver.select import Select
from src.core.driver.tabs import TabControl
from src.core.driver.wait import Wait
from src.core.driver.click import Click

logger = getLogger("WebDriver")

class WebDriverSession:
    def __init__(self):
        self.driver = None
        self.default_wait_time = 10
        self.undetected = False 

        self.nav = None
        self.find = None
        self.click = None
        self.wait = None
        self.input = None
        self.filter = None
        self.read = None
        self.tabControl = None
        self.select = None
        self.misc = None
         
    def __del__(self):
        if (self.driver):
            self.driver.quit()

    def is_alive(self):
        return (not(self.driver == None))

    def setUndetected(self, b):
        self.undetected = b

    def start(self):
        result = False

        options = self._getOptions()
        if (options):
            try:
                if self.undetected:
                    self.driver = uc.Chrome(options=options)
                else:
                    self.driver = webdriver.Chrome(options=options)
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
                result = True
            except SessionNotCreatedException as e:
                if e.msg:
                    logger.debug("WebDriver creation error:\n{}".format(e.msg))
                    if "this version of chromedriver only supports" in e.msg.lower(): # is it a version error?
                        current_version, expected_version = self.__get_versions_from_error_msg(e.msg)
                        logger.critical("Chrome outdated.\nYour version: {}\nRequired version: {}".format(current_version, expected_version))

        return result

    def set_default_wait_time(self, wait_time):
        self.default_wait_time = wait_time
        logger.debug(f"default wait time set to {wait_time}")

    def _getOptions(self):
        options = uc.ChromeOptions() if self.undetected else Options()
        if (options):
            downloadPath = str((ROOT / 'data' / 'dls').resolve())

            # set options for downloading
            prefs = {
                "download.default_directory": downloadPath,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": False,
                "profile.default_content_setting_values.automatic_downloads": 1,
                "profile.default_zoom_level_value": 2.0,  # very zoomed in
            }

            options.add_experimental_option("prefs", prefs)
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
        else:
            logger.critical("Failed to load chrome options")
            options = None

        return options

    def __get_versions_from_error_msg(self, msg):
        """
        returns tuple (current_version, expected_version)
        """

        current_version = "0.0.0.0"
        expected_version = "000"

        current_version_pattern = r"Current browser version is (\d+\.\d+\.\d+\.\d+);"
        expected_version_pattern = r"This version of ChromeDriver only supports Chrome version (\d+)\n"

        m = re.search(current_version_pattern, msg)
        if (m):
            current_version = m.group(1)

        m = re.search(expected_version_pattern, msg)
        if (m):
            expected_version = m.group(1)

        return (current_version, expected_version)
