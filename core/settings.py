import json
from core.utils import PROJ_FOLDER

settings = {
    "ignore_old": True,
    "day_diff": 3,
    "clear_downloads": False,
    "debug": False,
    "scrape": {
            "eshipper": True,
            "ems": True,
            "freightcom": True,
    },
    "track": {
            "canada post": True,
            "canpar": True,
            "fedex": True,
            "purolator": True,
            "ups": True,
    },
}

def load_settings() -> None:
    global settings
    with open(PROJ_FOLDER / "settings.json", 'r') as f:
        settings = json.load(f)

def check_settings_exists() -> bool:
    from os.path import exists as file_exists
    return file_exists(PROJ_FOLDER / "settings.json")

def create_settings_file() -> None:
    with open(PROJ_FOLDER / "settings.json", 'w') as f:
        json.dump(settings, f, indent=4)

def write_to_settings(d: dict):
    assert _check_dict(d)

    with open(PROJ_FOLDER / "settings.json", 'w') as f:
        json.dump(d, f, indent=4)

def _check_dict(d: dict) -> bool:
    with open(PROJ_FOLDER / "settings.json", 'r') as f:
        settings = json.load(f)
    
    for key in settings:
        if key not in d:
            return False
    
    return True


