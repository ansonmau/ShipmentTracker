from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from log import getLogger

logger = getLogger()

ELEMENT_TYPES = {
        'id': By.ID,
        'css': By.CSS_SELECTOR,
        'xpath': By.XPATH
}

class WebDriverSession:
        def __init__(self):
                self.driver = webdriver.Chrome()
                self.driver.maximize_window()
        
        def __del__(self):
                self.driver.quit()
        
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
                        element = parentElement.find_element(target_elem_type, target_path)
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
                        elements = parentElement.find_elements(target_elem_type, target_path)
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
                
        def click(self, pathTuple):
                element = self.find(pathTuple)

                assert element is not None
                element.click()
        
        def waitForPageLoad(self):
                WebDriverWait(self.driver, 10).until(
                        lambda d: d.execute_script("return document.readyState") == "complete"
                )
        
        def waitFor(self, pathTuple):
                self.find(pathTuple)