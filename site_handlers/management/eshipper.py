from driver import WebDriverSession, ELEMENT_TYPES
paths = {
        "username_input": (ELEMENT_TYPES['id'], 'username'),
        "password_input": (ELEMENT_TYPES['id'], 'password'),
        "login_button": (ELEMENT_TYPES['css'], '[aria-label="Login Button"]'),
        
}


def login(sesh: WebDriverSession):
        sesh.get("https://ww2.eshipper.com/login")
        username_element = sesh.find(paths['username_input'])
        password_element = sesh.find(paths['password_input'])
        login_button_element = sesh.find(paths['login_button'])


def scrape(sesh: WebDriverSession):
        pass