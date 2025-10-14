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
                                                                                                        
