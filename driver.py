from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

class WebDriverSession:
        def __init__(self):
                self.driver = webdriver.Chrome()
                self.driver.maximize_window()
        
        def get(self, url):
                self.driver.get(url)
        
        def find(self, id=None, xpath=None, css=None):
                try:
                        if id is not None:
                                element = self.driver.find_element(By.ID, id)
                        if xpath is not None:
                                element = self.driver.find_element(By.XPATH, xpath)
                        if css is not None:
                                element = self.driver.find_element(By.CSS_SELECTOR, css)
                except NoSuchElementException:
                        element = None
                
                return element

        def inputText(self, txt, xpath):
                pass
