import glob
import csv
import pathlib

def parse():
        dl_files = getFiles()

        assert len(dl_files) > 0
        
        # should only be one file
        csv_file = dl_files[0]
        

        pass

def check():
        files = getFiles()
        return True if len(files)>0 else False

def getFiles():
        proj_folder = pathlib.Path(__file__).resolve().parent.parent
        dl_folder = proj_folder / 'dls'

        files = dl_folder.glob("Track*.csv") # returns generator
        files = list(files)

        return files

def save(data):
        proj_folder = pathlib.Path(__file__).resolve().parent.parent
        file_path = proj_folder / 'data' / 'delivery_data.txt'

        with open(file_path, 'w') as f:
                f.write(data)