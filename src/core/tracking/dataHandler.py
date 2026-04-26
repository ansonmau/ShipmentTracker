import json
from core.utils import ROOT

class Handler:
    file_path = ROOT / 'data' / 'tracking_data.json'

    def __init__(self):
        self.canada_post = []
        self.purolator = []
        self.ups = []
        self.fedex = []
        self.canpar = []

        self.d = {
            'canada post': self.canada_post,
            'canpar': self.canpar,
            'fedex': self.fedex,
            'purolator': self.purolator,
            'ups': self.ups   
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
        with open(Handler.file_path, 'r') as fh:
            d = json.load(fh)

        self.canada_post.extend(d["canada post"])
        self.purolator.extend(d["purolator"])
        self.ups.extend(d["ups"])
        self.fedex.extend(d["fedex"])
        self.canpar.extend(d["canpar"])

    def save_to_file(self):
        with open(Handler.file_path, 'w') as fh:
            json.dump(self.d, fh, indent=4)

    def get_count(self, carrier=None):
        count = 0
        if (carrier):
            count += len(self.d[carrier])
        else:
            for c in self.d:
                count += len(self.d[c])
        return count

    def get_dict(self):
        return self.d


