import glob
import csv
import pathlib
from datetime import datetime, timedelta
import time
from core.log import getLogger

log = getLogger(__name__)

PROJ_FOLDER = pathlib.Path(__file__).resolve().parent.parent.parent


def parse(file_search_time=30):
        file = get_downloaded_file(file_search_time)
        
        # should only be one file
        file_path = str(file)
        with open(file_path, 'r') as file:
                file_dict = csv.DictReader(file)

                date_format = "%m/%d/%Y"
                day_diff = 30
                min_date = calc_oldest_day(day_diff)
                data = {}

                for entry in file_dict:
                        entry_date = datetime.strptime(entry["Ship Date"], date_format)
                        if entry_date < min_date:
                                break
                        
                        status = entry['Status']
                        if status not in ["IN TRANSIT", "READY FOR SHIPPING"]:
                                continue
                        
                        tracking_num = entry["Tracking#"]
                        carrier = entry["Carrier"]

                        if carrier in data:
                                data[carrier].append(tracking_num)
                        else:
                                data[carrier] = [tracking_num]
                
        save_data(data)
        return data

def calc_oldest_day(day_diff):
        curr_date = datetime.today()
        min_date = curr_date - timedelta(days = day_diff)
        return min_date   

def get_downloaded_file(search_time = 30):
        end_time = time.time() + search_time

        files = check_downloads()
        og_file_num = len(files)
        while len(files) <= og_file_num and time.time() < end_time:
                files = check_downloads()

        return files[0]

def check_downloads():
        dl_folder = PROJ_FOLDER/'dls'

        files = dl_folder.glob("Track*.csv") # returns generator

        return list(files)

def save_data(data):
        file_path = PROJ_FOLDER/'data'/'delivery_data.txt'

        with open(str(file_path), 'w') as f:
                for key in data:
                        f.write(key + '\n')
                        if len(data[key]) == 0:
                                f.write('\t' + "N/A" + '\n')
                        for val in data[key]:
                                f.write('\t' + val + '\n')