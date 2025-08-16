from driver import WebDriverSession


ID = {
        "username_input": "username",
        "password_input": "password",
}

CSS = {
        "login_button": "[aria-label=\"Login Button\"]"
}

XPATH = {

}


def login(sesh: WebDriverSession):
        sesh.get("https://ww2.eshipper.com/login")
        username_element = sesh.find(id = ID['username_input'])
        password_element = sesh.find(id = ID['password_input'])
        login_button_element = sesh.find(css = CSS['login_button'])
        

def scrape(sesh: WebDriverSession):
        pass