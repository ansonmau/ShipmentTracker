import driver
from dotenv import load_dotenv
from os import getenv
import site_handlers.management.eshipper as eshipper
from log import getLogger
logger = getLogger()

def main():
        load_dotenv(dotenv_path="./venv/keys.env")

        sesh = driver.WebDriverSession()
        eshipper.login(sesh)
        eshipper.scrape(sesh)

        input()
        pass
        


if __name__ == "__main__":
        main()