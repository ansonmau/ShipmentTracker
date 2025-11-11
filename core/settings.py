import json

settings = {
        "ignore_old": True,
    "day_diff": 3,
    "clear_downloads": False,
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
    with open("settings.json", 'r') as f:
        settings = json.load(f)

def check_settings_exists() -> bool:
    from os.path import exists as file_exists
    return file_exists("settings.json")

def create_settings_file() -> None:
    with open("settings.json", 'w') as f:
        json.dump(settings, f, indent=4)
