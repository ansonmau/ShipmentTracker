import json
from core.utils import ROOT

class TrackingDataHandler:
    file_path = ROOT / 'data' / 'tracking_data.json'
    canada_post = []
    purolator = []
    ups = []
    fedex = []
    canpar = []

    d = {
        'canada post': canada_post,
        'canpar': canpar,
        'fedex': fedex,
        'purolator': purolator,
        'ups': ups   
    }

    def add_shipment(self, carrier_name, tracking_number):
        shipment_list = self.d[carrier_name.lower()]
        shipment_list.append(tracking_number)

    def remove_shipment(self, carrier_name, tracking_number):
        shipment_list = self.d[carrier_name.lower()]
        shipment_list.remove(tracking_number)

    def check_shipment_exists(self, carrier_name, tracking_number):
        shipment_list = self.d[carrier_name.lower()]
        return tracking_number in shipment_list

    def get_tracking_numbers(self, carrier_name):
        return self.d[carrier_name.lower()]

    def read_from_file(self):
        with open(TrackingDataHandler.file_path, 'r') as fh:
            d = json.load(fh)

        TrackingDataHandler.canada_post.extend(d["canada_post"])
        TrackingDataHandler.purolator.extend(d["purolator"])
        TrackingDataHandler.ups.extend(d["ups"])
        TrackingDataHandler.fedex.extend(d["fedex"])
        TrackingDataHandler.canpar.extend(d["canpar"])

    def save_to_file(self):
        with open(TrackingDataHandler.file_path, 'w') as fh:
            json.dump(TrackingDataHandler.d, fh, indent=4)

    def get_dict(self):
        return self.d


