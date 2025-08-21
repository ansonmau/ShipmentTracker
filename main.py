import core.driver as driver
from dotenv import load_dotenv
import os
import site_handlers.management.eshipper as eshipper_sh
import site_handlers.delivery.fedex as fedex_sh
import file_handlers.eshipper as eshipper_fh
from core.log import getLogger

logger = getLogger()

def main():
        initialize()
        
        sesh = driver.WebDriverSession()
        # eshipper_sh.scrape(sesh)
        
        # data = eshipper_fh.parse()
        # print(data)
        
        fedex_sh.scrape(sesh)

        input()
        pass
        
def initialize():
        loadEnvFile()
        createDownloadsFolder()

def createDownloadsFolder():
        dl_dir = os.path.abspath("./dls")
        os.makedirs(dl_dir, exist_ok=True)

def loadEnvFile():
        load_dotenv(dotenv_path="./venv/keys.env")

def cleanup():
        clearDLFolder()

def clearDLFolder():
        pass

if __name__ == "__main__":
        main()