import glob
import csv
import pathlib
from datetime import datetime, timedelta
import time
from core.log import getLogger

log = getLogger(__name__)

def parse():
        eshipper_files = waitForFile(cd = 30)
        assert len(eshipper_files) == 1
        
        date_format = "%m/%d/%Y"
        day_diff = 30
        min_date = getMinDate(day_diff)

        # should only be one file
        file_path = str(eshipper_files[0])
        file = open(file_path, 'r')
        file_dict = csv.DictReader(file)

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
        
        
        file.close()
        save(data)

        return data

def getMinDate(day_diff):
        curr_date = datetime.today()
        min_date = curr_date - timedelta(days = day_diff)
        return min_date   


def check():
        files = getEshipperFiles()
        return True if len(files)>0 else False

def waitForFile(cd = 30):
        end_time = time.time() + cd

        files = getEshipperFiles()
        while time.time() < end_time and len(files) == 0:
                files = getEshipperFiles()

        return files

def getEshipperFiles():
        proj_folder = pathlib.Path(__file__).resolve().parent.parent
        dl_folder = proj_folder / 'dls'

        files = dl_folder.glob("Track*.csv") # returns generator
        files = list(files)

        return files

def save(data):
        proj_folder = pathlib.Path(__file__).resolve().parent.parent
        file_path = proj_folder / 'data' / 'delivery_data.txt'

        with open(str(file_path), 'w') as f:
                f.write(str(data))