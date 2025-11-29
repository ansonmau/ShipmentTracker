import glob
import csv
import pathlib
from datetime import datetime, timedelta
import time
from core.log import getLogger
from core.settings import settings
from core.utils import PROJ_FOLDER

log = getLogger(__name__)



def parse(file_search_time=30):
    data = {
        "UPS": [],
        "Canpar": [],
        "Purolator": [],
        "Canada Post": [],
        "Fedex": [],
    }
    
    file = get_downloaded_file(file_search_time)

    # should only be one file
    file_path = str(file)
    with open(file_path, "r") as file:
        file_dict = csv.DictReader(file)

        date_format = "%m/%d/%Y"
        min_date = calc_oldest_day(settings['day_diff'])

        for entry in file_dict:
            entry_date = datetime.strptime(entry["Ship Date"], date_format)
            if entry_date < min_date:
                break

            status = entry["Status"]
            if status not in ["IN TRANSIT", "READY FOR SHIPPING"]:
                continue

            tracking_num = entry["Tracking#"]
            carrier = standardize_carrier_name(entry["Carrier"])

            data[carrier].append(tracking_num)

    return data


def calc_oldest_day(day_diff):
    curr_date = datetime.today()
    min_date = curr_date - timedelta(days=day_diff)
    return min_date


def get_downloaded_file(search_time=30):
    end_time = time.time() + search_time

    files = check_downloads()
    og_file_num = len(files)
    while len(files) <= og_file_num and time.time() < end_time:
        files = check_downloads()

    return files[0]


def check_downloads():
    dl_folder = PROJ_FOLDER / "dls"

    files = dl_folder.glob("Track*.csv")  # returns generator

    return list(files)

def standardize_carrier_name(carrier_name):
    translator = {
        "UPS": "UPS",
        "Canpar": "Canpar",
        "Purolator": "Purolator",
        "Canada Post": "Canada Post",
        "Federal Express": "Fedex"
    }

    return translator[carrier_name]
