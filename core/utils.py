import pathlib
from datetime import datetime
import json
import sys

def _get_proj_folder():
    if getattr(sys, "frozen", False):
        return pathlib.Path(sys.executable).parent
    
    return pathlib.Path(pathlib.Path(__file__).resolve().parent.parent)

PROJ_FOLDER = _get_proj_folder()

def merge_dict_lists(dict_1, dict_2):
    for key in dict_2:
        assert key in dict_1
        # merge without duplicates
        for val in dict_2[key]:
            if val not in dict_1[key]:
                dict_1[key].append(val)

def save_tracking_data(data: dict, file_name="tracking_data") -> None:
    file_path = PROJ_FOLDER / "data" / f"{file_name}.json"
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def read_tracking_data(file_name="tracking_data") -> dict:
    file_path = PROJ_FOLDER / "data" / f"{file_name}.json"
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data
                                                                                                        
def generate_tracking_link(carrier, tracking_num) -> str:
    carrier_to_link = {
            "Canada Post": f"https://www.canadapost-postescanada.ca/track-reperage/en#/search?searchFor={tracking_num}",
            "Purolator": f"https://www.purolator.com/en/shipping/tracker?pin={tracking_num}",
            "Fedex": f"https://www.fedex.com/fedextrack/?trknbr={tracking_num}",
            "Canpar": f"https://www.canpar.com/en/tracking/delivery_options.htm?barcode={tracking_num}",
            "UPS": f"https://www.ups.com/track?trackingNumber={tracking_num}",
            }  

    if carrier in carrier_to_link:
        return carrier_to_link[carrier]

    return ''

def create_folder(name):
    from os import makedirs
    folder = PROJ_FOLDER / name
    makedirs(folder, exist_ok=True)

def create_file(dir: pathlib.Path | str, name: str | None = None):
    dir = pathlib.Path(dir)

    full_path = dir if name is None else dir / name
    full_path.touch()

