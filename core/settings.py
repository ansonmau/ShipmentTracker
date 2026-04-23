import json
from core.utils import ROOT

class Settings:
    file_path = ROOT / 'settings.json'

    settings = {
        "ignore_already_tracked": True,
        "day_diff": 3,
        "default_wait_time": 5,
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


