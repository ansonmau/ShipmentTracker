import pathlib

PROJ_FOLDER = pathlib.Path(__file__).resolve().parent.parent

def update_data(data_dict, new_dict):
    for key in new_dict:
        if key in data_dict:
            data_dict[key] = data_dict[key] + new_dict[key]
            

def save_data(data):
    file_path = PROJ_FOLDER / "data" / "tracking_data.txt"

    with open(str(file_path), "w") as f:
            for key in data:
                f.write(key + "\n")
                if len(data[key]) == 0:
                    f.write("\t" + "N/A" + "\n")
                for val in data[key]:
                    f.write("\t" + val + "\n")
                                                                                                        
def save_results(results) -> None:
    success_file = PROJ_FOLDER / "report" / "success.txt"
    fail_file = PROJ_FOLDER / "report" / "failed.txt"

    with open(str(success_file), "w") as f:
        for result in results["success"]:
            carrier = result[0]
            tracking_num = result[1]
            f.write(f"[SUCCESS] {carrier} #{tracking_num} ----- {generate_tracking_link(carrier, tracking_num)}" + '\n')

    with open(str(fail_file), "w") as f:
        for result in results["fail"]:
            carrier = result[0]
            tracking_num = result[1]
            f.write(f"[FAIL] {carrier} #{tracking_num} ----- {generate_tracking_link(carrier, tracking_num)}" + '\n')
        for result in results["crash"]:
            carrier = result[0]
            tracking_num = result[1]
            f.write(f"[CRASH (FAIL)] {carrier} #{tracking_num} ----- {generate_tracking_link(carrier, tracking_num)}" + '\n')

def generate_tracking_link(carrier, tracking_num):
    carrier_to_link = {
            "canada post": f"https://www.canadapost-postescanada.ca/track-reperage/en#/search?searchFor={tracking_num}",
            "purolator": f"https://www.purolator.com/en/shipping/tracker?pin={tracking_num}",
            "fedex": f"https://www.fedex.com/fedextrack/?trknbr={tracking_num}",
            "canpar": f"https://www.canpar.com/en/tracking/delivery_options.htm?barcode={tracking_num}",
            "ups": f"https://www.ups.com/track?trackingNumber={tracking_num}",
            }  

    return carrier_to_link[carrier]

def create_folder(name):
    from os import makedirs
    folder = PROJ_FOLDER / name
    makedirs(folder, exist_ok=True)
    

