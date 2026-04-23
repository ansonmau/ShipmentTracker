import csv
from datetime import datetime, timedelta
import time
from core.log import getLogger
from core.settings import Settings
from core.utils import ROOT

logger = getLogger(__name__)

def parse(file_search_time=30):
    results = []
    file = get_downloaded_file(file_search_time)

    if file == None:
        logger.info("Failed to find eshipper file")
        return results

    logger.info("Eshipper file found")
    # should only be one file
    file_path = str(file)
    with open(file_path, "r") as file:
        file_dict = csv.DictReader(file)

        date_format = "%m/%d/%Y"
        min_date = calc_oldest_day(Settings.get_settings()['day_diff'])
        logger.info("Searching from date: {}".format(min_date))

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


def get_downloaded_file(search_time=30):
    end_time = time.time() + search_time

    files = []
    while len(files) == 0 and time.time() < end_time:
        files = check_downloads()

    if len(files) == 0:
        logger.info("Failed to find downloaded eshipper file")
        return None

    return files[0]


def check_downloads():
    dl_folder = ROOT / "dls"
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
