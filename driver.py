from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
                        element = None
                

                return element
        
        def findFromParent(self, parentTuple, targetTuple, wait = 5):
                parent_elem_type, parent_path = parentTuple
                target_elem_type, target_path = targetTuple

                parent_element = self.find(parent_elem_type, parent_path)

                assert parent_element is not None
                try:
                        element = parent_element.find_element(target_elem_type, target_path)
                except NoSuchElementException:
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
                        elements = None
                

                return elements

        def findAllFromParent(self, parentTuple, targetTuple, wait = 5):
                parent_elem_type, parent_path = parentTuple
                target_elem_type, target_path = targetTuple

                parent_element = self.find(parent_elem_type, parent_path)

                assert parent_element is not None
                try:
                        elements = parent_element.find_elements(target_elem_type, target_path)
                except NoSuchElementException:
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