from selenium.webdriver.common.by import By

class ElementTypes:
    id = By.ID
    css = By.CSS_SELECTOR
    xpath = By.XPATH
    tag = By.TAG_NAME

class Locator:
    def __init__(self, element_type = By.ID, element_locator = ""):
        self.element_type = element_type
        self.element_locator = element_locator

    def get_type(self):
        return self.element_type

    def get_locator(self):
        return  self.element_locator


