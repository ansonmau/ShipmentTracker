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

logger = getLogger(__name__)

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
                options = self._getOptions(undetected=undetected)
                if undetected:
                        self.driver = uc.Chrome(options=options)
                else:
                        self.driver = webdriver.Chrome(options=options)
                self.driver.maximize_window()

                self.find = find(self)
                self.click = click(self)
                self.waitFor = waitFor(self)
                self.input = input(self)
                self.filter = filter(self)
                self.read = read(self)
                self.iframe = iframe(self)
                self.tabControl = tabControl(self)
        
        
        def __del__(self):
                self.driver.quit()
        
        def _getOptions(self, undetected = False):
                relative_path = "./dls"
                downloadPath = os.path.abspath(relative_path)

                # set options for downloading
                prefs = {
                        "download.default_directory": downloadPath,
                        "download.prompt_for_download": False,
                        "download.directory_upgrade": True,
                        "safebrowsing.enabled": True
                }

                if undetected:
                        options = uc.ChromeOptions()
                else:
                        options = Options()

                options.add_experimental_option("prefs", prefs)

                return options
                
        def get(self, url):
                self.driver.get(url)

        def injectJS(self, script):
                self.driver.execute_script(script)

        def scrollToElement(self, element):
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        
        def getShadowRoot(self, shadow_root_parent):
                return self.driver.execute_script("return arguments[0].shadowRoot", shadow_root_parent)


class find:
        def __init__(self, sesh : WebDriverSession):
                self.sesh = sesh

        def path(self, targetTuple, wait = 5):
                elem_type, path = targetTuple

                try:
                        element = WebDriverWait(self.sesh.driver, wait).until(
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
        
        def fromParent(self, parentElement, targetTuple, wait = 5):
                target_elem_type, target_path = targetTuple

                assert parentElement is not None
                try:
                        element = WebDriverWait(self.sesh.driver, wait).until(
                                lambda d: parentElement.find_element(target_elem_type, target_path)
                        )
                except NoSuchElementException:
                        logger.error("could not find {}".format(targetTuple))
                        element = None
                except TimeoutException:
                        logger.error("timed out finding {}".format(targetTuple))
                        element = None
                
                return element

        def all(self, targetTuple, wait = 5):
                elem_type, path = targetTuple

                try:
                        elements = WebDriverWait(self.sesh.driver, wait).until(
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

        def allFromParent(self, parentElement, targetTuple, wait = 5):
                target_elem_type, target_path = targetTuple

                assert parentElement is not None
                try:
                        elements = WebDriverWait(self.sesh.driver, wait).until(
                                lambda d: parentElement.find_elements(target_elem_type, target_path)
                        )
                except NoSuchElementException:
                        logger.error("could not find {}".format(targetTuple))
                        elements = None
                except TimeoutException:
                        logger.error("timed out finding {}".format(targetTuple))
                        elements = None

                return elements

class filter:
        def __init__(self, sesh: WebDriverSession):
                self.sesh = sesh

        def byText(self, element_list, txt):
                elmnts = []
                for elmnt in element_list:
                        if self.sesh.read.textFromElement(elmnt) == txt:
                                elmnts.append(elmnt)
                return elmnts


class waitFor:
        def __init__(self, sesh: WebDriverSession):
                self.sesh = sesh
                
        def pageLoad(self):
                WebDriverWait(self.sesh.driver, 10).until(
                        lambda d: d.execute_script("return document.readyState") == "complete"
                )
        
        def path(self, pathTuple, wait = 5):
                self.sesh.find.path(pathTuple, wait=wait)
        
        def elementInParent(self, parent, pathTuple):
                self.sesh.find.fromParent(parent, pathTuple)
        
        def function(self, fnc):
                try:
                        WebDriverWait(self.sesh.driver, 10).until(fnc)
                except TimeoutException:
                        logger.error("waiting for function failed")
                        return False
                
                return True

        def hardWait(self, wait_time):
                time.sleep(wait_time)

class input:
        def __init__(self, sesh: WebDriverSession):
                self.sesh = sesh
        
        def _sendKeys(self, target_element, keys):
                assert target_element is not None

                self.sesh.click.element(target_element)
                randomWait()
                target_element.send_keys(keys)

        def element(self, element, txt):
                self._sendKeys(element, txt)

        def path(self, pathTuple, txt):
                element = self.sesh.find.path(pathTuple)

                assert element is not None 
                self._sendKeys(element, txt)
        
        def fromParent(self, parent, pathTuple, txt):
                elmnt = self.sesh.find.fromParent(parent, pathTuple)
                self._sendKeys(elmnt, txt)

                
class click:
        def __init__(self, sesh: WebDriverSession):
                self.sesh = sesh
        
        def _click_element(self, target_element):
                assert target_element is not None

                randomWait()
                target_element.click()

        def element(self, elmnt): 
                self._click_element(elmnt)
                
        def path(self, pathTuple):
                element = self.sesh.find.path(pathTuple)

                self._click_element(element)
        
        def element_by_js(self, element):
                self.sesh.injectJS("arguments[0].scrollIntoView({block:'center'});", element)
                self.sesh.injectJS("arguments[0].click();", element)

        def fromParent(self, parent, pathTuple):
                element = self.sesh.find.fromParent(parent, pathTuple)

                self._click_element(element)
        
class read:
        def __init__(self, sesh: WebDriverSession):
                self.sesh = sesh
        
        def text(self, targetTuple):
                element = self.sesh.find.path(targetTuple)

                return self._getElementText(element)
        
        def textFromElement(self, element):
                return self._getElementText(element)

        def _getElementText(self, element):
                assert element is not None
                return element.text

class iframe:
        def __init__(self, sesh: WebDriverSession):
                self.sesh = sesh
        
        def reset(self):
                self.sesh.driver.switch_to.default_content()
        
        def select(self, iframe_element):
                self.sesh.driver.switch_to.frame(iframe_element)
        
class tabControl:
        def __init__(self, sesh: WebDriverSession):
                self.sesh = sesh
        
        def _waitForNewTab(self, wait=5):
                curr_num_tabs = len(self.sesh.driver.window_handles)
                try:
                        WebDriverWait(self.sesh.driver, wait).until(lambda x: len(x.window_handles) > curr_num_tabs)
                        return True
                except TimeoutException:
                        logger.debug("New tab did not appear")

                return False
        
        def getNumTabs(self):
                return len(self.getTabs())

        def getTabs(self):
                return self.sesh.driver.window_handles

        def getCurrentTab(self):
                return self.sesh.driver.current_window_handle

        def focusNewestTab(self):
                self._waitForNewTab()
                tabs = self.getTabs()
                self.sesh.driver.switch_to.window(tabs[-1])