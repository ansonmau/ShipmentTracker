from driver import WebDriverSession

def login(sesh: WebDriverSession):
        sesh.get("https://ww2.eshipper.com/login")
        

def scrape(sesh: WebDriverSession):
