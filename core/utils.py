def update_data(data_dict, new_dict):
    for key in new_dict:
        if key in data_dict:
            data_dict[key] = data_dict[key] + new_dict[key]
