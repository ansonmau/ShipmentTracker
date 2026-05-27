import csv
from datetime import datetime, timedelta
import time
from src.core.log import getLogger
from src.core.settings import Settings
from src.core.utils import ROOT

logger = getLogger("eship-file-handler")

class Handler:
    def __init__(self):
        self.downloads_folder = ROOT / 'data' / 'dls'
        self.wait_time = 120
        self.file = None

    def set_wait_time(self, wait_time):
        self.wait_time = wait_time

    def wait_for_file_download(self):
        """
        desc:
            checks once per sec for chrome to finish downloading the file.
            checks for crdownload suffix
        """
        download_in_progress    =   True
        end_time                =   time.time() + self.wait_time
        while ((time.time() < end_time) and (download_in_progress)):
            download_in_progress = False
            file_sfxs = [x.suffix for x in self._get_files()]
            if (not(file_sfxs)) or (".crdownload" in file_sfxs):
                download_in_progress = True
                time.sleep(1)
                continue 
            else:
                self.file = self._get_files()[0]

        return False if download_in_progress else True
    
    def _get_files(self) -> list:
        files = self.downloads_folder.glob("*")  # returns generator
        return list(files)

    def parse(self) -> list:
        if (not(self.file)):
            logger.debug(" Could not parse because file not set. (forgot to call wait_for_file_download?)")
            return []

        results = []
        file_path = str(self.file)
        with open(file_path, "r") as file:
            file_dict = csv.DictReader(file)
            date_format = "%m/%d/%Y"
            min_date = calc_oldest_day(Settings.get_settings()['extras']['day_diff'])

            for entry in file_dict:
                entry_date = datetime.strptime(entry["Ship Date"], date_format)
                if entry_date < min_date:
                    break

                status = entry["Status"]
                if status not in ["IN TRANSIT", "READY FOR SHIPPING"]:
                    continue

                tracking_num = entry["Tracking#"]
                carrier = standardize_carrier_name(entry["Carrier"])

                results.append((carrier, tracking_num))

        return results


def calc_oldest_day(day_diff):
    curr_date = datetime.today()
    min_date = curr_date - timedelta(days=day_diff)
    return min_date

def standardize_carrier_name(carrier_name):
    translator = {
        "UPS": "UPS",
        "Canpar": "Canpar",
        "Purolator": "Purolator",
        "Canada Post": "Canada Post",
        "Federal Express": "Fedex"
    }

    return translator[carrier_name]
