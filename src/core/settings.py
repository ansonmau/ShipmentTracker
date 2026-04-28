import json
from src.core.utils import ROOT

class Settings:
    file_path = ROOT / 'settings.json'

    settings = {
        "scrape": {
            "eshipper": False,
            "ems": False,
            "freightcom": False
        },
        "track": {
            "canada post": False,
            "canpar": False,
            "fedex": False,
            "purolator": False,
            "ups": False
        },
        "extras": {
            "day_diff": 5,
            "default_wait_time": 5,
            "ignore_already_tracked" : False, 
            "debug_mode": False,
            "reuse_data": False
        }
    }

    

    @staticmethod
    def get_settings():
        return Settings.settings

    @staticmethod
    def load_from_file() -> None:
        if (Settings.file_exists()):
            with open(Settings.file_path, 'r') as f:
                Settings.settings.update(json.load(f))

    @staticmethod
    def file_exists() -> bool:
        from os.path import exists as file_exists
        return file_exists(Settings.file_path)

    @staticmethod
    def write_to_file():
        with open(Settings.file_path, 'w') as f:
            json.dump(Settings.settings, f, indent=4)


