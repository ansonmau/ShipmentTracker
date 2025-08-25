import core.driver as driver
from dotenv import load_dotenv
import os
import site_handlers.management.eshipper as eshipper_sh
import file_handlers.eshipper as eshipper_fh
import site_handlers.delivery.canadapost as canpost
from core.log import getLogger


logger = getLogger()

def main():
        initialize()
        sesh = driver.WebDriverSession(undetected=True)
        #eshipper_sh.scrape(sesh)
        
        data = eshipper_fh.parse()
        print(canpost.track(sesh, data['Canada Post'][10:12]))
        
        # fedex_sh.scrape(sesh)

        print('done')
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