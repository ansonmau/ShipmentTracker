from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import time
import random
import os

from core.log import getLogger

logger = getLogger()

ELEMENT_TYPES = {
        'id': By.ID,
        'css': By.CSS_SELECTOR,
        'xpath': By.XPATH,
        'tag': By.TAG_NAME,
}

def randomWait(min = 0.5, max = 1.5):
        delay = random.uniform(min,max)
        time.sleep(delay)

class WebDriverSession:
        def __init__(self, undetected=False):
                options = self._getOptions()
                if undetected:
                        self.driver = uc.Chrome(options=options)
                else:
                        self.driver = webdriver.Chrome(options=options)

                self.driver.maximize_window()
                
        
        def __del__(self):
                self.driver.quit()
        
        def _getOptions(self):
                relative_path = "./dls"
                downloadPath = os.path.abspath(relative_path)

                prefs = {
                        "download.default_directory": downloadPath,
                        "download.prompt_for_download": False,
                        "download.directory_upgrade": True,
                        "safebrowsing.enabled": True
                }

                options = Options()
                options.add_experimental_option("prefs", prefs)

                return options
                
        def get(self, url):
                self.driver.get(url)
        
        def find(self, targetTuple, wait = 5):
                elem_type, path = targetTuple

                try:
                        element = WebDriverWait(self.driver, wait).until(
                                        EC.presence_of_element_located(
                                                        (elem_type, path)
                                        )
                        )
                except NoSuchElementException:
                        logger.error("could not find {}".format(targetTuple))
                        element = None
                except TimeoutException:
                        logger.error("timed out finding {}".format(targetTuple))
                        element = None
                

                return element
        
        def findFromParent(self, parentElement, targetTuple, wait = 5):
                target_elem_type, target_path = targetTuple

                assert parentElement is not None
                try:
                        element = WebDriverWait(self.driver, wait).until(
                                lambda d: parentElement.find_element(target_elem_type, target_path)
                        )
                except NoSuchElementException:
                        logger.error("could not find {}".format(targetTuple))
                        element = None
                except TimeoutException:
                        logger.error("timed out finding {}".format(targetTuple))
                        element = None
                
                return element

        def findAll(self, targetTuple, wait = 5):
                elem_type, path = targetTuple

                try:
                        elements = WebDriverWait(self.driver, wait).until(
                                        EC.presence_of_all_elements_located(
                                                        (elem_type, path)
                                        )
                        )
                except NoSuchElementException:
                        logger.error("could not find {}".format(targetTuple))
                        elements = None
                except TimeoutException:
                        logger.error("timed out finding {}".format(targetTuple))
                        elements = None
                

                return elements

        def findAllFromParent(self, parentElement, targetTuple, wait = 5):
                target_elem_type, target_path = targetTuple

                assert parentElement is not None
                try:
                        elements = WebDriverWait(self.driver, wait).until(
                                lambda d: parentElement.find_elements(target_elem_type, target_path)
                        )
                except NoSuchElementException:
                        logger.error("could not find {}".format(targetTuple))
                        elements = None
                except TimeoutException:
                        logger.error("timed out finding {}".format(targetTuple))
                        elements = None

                return elements



        def inputText(self, pathTuple, txt):
                element = self.find(pathTuple)

                assert element is not None
                element.send_keys(txt)
        
        def element_inputText(self, element, txt):
                element.send_keys(txt)

                
        def click(self, pathTuple):
                element = self.find(pathTuple)

                assert element is not None
                randomWait()
                element.click()
        
        def clickFromParent(self, parent, pathTuple):
                element = self.findFromParent(parent, pathTuple)

                assert element is not None
                randomWait()
                element.click()
        
        def element_click(self, element):
                assert element is not None
                randomWait()
                element.click()
        
        def waitForPageLoad(self):
                WebDriverWait(self.driver, 10).until(
                        lambda d: d.execute_script("return document.readyState") == "complete"
                )
        
        def waitFor(self, pathTuple, wait = 5):
                self.find(pathTuple, wait=wait)
        
        def waitForFromParent(self, parent, pathTuple):
                self.findFromParent(parent, pathTuple)
        
        def getText(self, targetTuple):
                element = self.find(targetTuple)
                return element.text

        def injectJS(self, script):
                self.driver.execute(script)