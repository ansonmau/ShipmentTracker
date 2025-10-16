from main import initialize
from core.driver import WebDriverSession
from handlers.site_handlers.management import freightcom

def main():
    initialize.run()
    sesh = WebDriverSession(True)

    freightcom.scrape(sesh)

