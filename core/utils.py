import pathlib
from datetime import datetime
import json

PROJ_FOLDER = pathlib.Path(__file__).resolve().parent.parent

def update_tracking_data(data_dict, new_dict):
    for key in new_dict:
        if key in data_dict:
            data_dict[key] = data_dict[key] + new_dict[key]

def save_tracking_data(data: dict, file_name="tracking_data") -> None:
    file_path = PROJ_FOLDER / "data" / f"{file_name}.json"
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def read_tracking_data(file_name="tracking_data") -> dict:
    file_path = PROJ_FOLDER / "data" / f"{file_name}.json"
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data
                                                                                                        
def generate_tracking_link(carrier, tracking_num):
    carrier_to_link = {
            "Canada Post": f"https://www.canadapost-postescanada.ca/track-reperage/en#/search?searchFor={tracking_num}",
            "Purolator": f"https://www.purolator.com/en/shipping/tracker?pin={tracking_num}",
            "Fedex": f"https://www.fedex.com/fedextrack/?trknbr={tracking_num}",
            "Canpar": f"https://www.canpar.com/en/tracking/delivery_options.htm?barcode={tracking_num}",
            "UPS": f"https://www.ups.com/track?trackingNumber={tracking_num}",
            }  

    return carrier_to_link[carrier]

def create_folder(name):
    from os import makedirs
    folder = PROJ_FOLDER / name
    makedirs(folder, exist_ok=True)
    

