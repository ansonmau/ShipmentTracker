import json

settings = {
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
