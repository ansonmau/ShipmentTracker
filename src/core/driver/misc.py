class Misc:
    def __init__(self, wds):
        self.wds = wds
        self.driver = wds.driver

    def injectJS(self, script):
        self.driver.execute_script(script)

    def scrollToElement(self, element, centered=False):
        if centered:
            self.driver.execute_script("arguments[0].scrollIntoView({block: \"center\", inline: \"nearest\"});", element)
        else:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    def getShadowRoot(self, shadow_root_parent):
        return self.driver.execute_script(
            "return arguments[0].shadowRoot", shadow_root_parent
        )

    def remove_element(self, element):
        self.driver.execute_script(
                "arguments[0].remove();", element
        )

    def maximize_window(self):
        self.driver.maximize_window()
