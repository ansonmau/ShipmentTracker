from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

ELEMENT_TYPES = {
        'id': 0,
        'css': 1,
        'xpath': 2
}

class WebDriverSession:
        def __init__(self):
                self.driver = webdriver.Chrome()
                self.driver.maximize_window()
        
        def __del__(self):
                self.driver.quit()
        
        def get(self, url):
                self.driver.get(url)
        
        def find(self, pathTuple):
                elem_type, path = pathTuple

                if elem_type == ELEMENT_TYPES['id']:
                        searchType = By.ID
                if elem_type == ELEMENT_TYPES['css']:
                        searchType = By.CSS_SELECTOR
                if elem_type == ELEMENT_TYPES['xpath']:
                        searchType = By.XPATH

                try:
                        element = self.driver.find_element(searchType, path)
                except NoSuchElementException:
                        element = None
                
                return element

        def inputText(self, txt, xpath):
                pass
