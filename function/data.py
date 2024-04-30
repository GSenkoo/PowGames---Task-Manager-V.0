import json

def get_data(file : str, data_path : str):
    if file == "config":
        file = "config.json"
    elif file == "db" or file == "database":
        file = "db/db.json"
    
    with open(file, encoding = "utf-8") as file:
        data = json.load(file)

    data_path = data_path.split("/")
    result = data

    for value in data_path:
        result = result[value]

    return result

def set_data(file : str, data_path : str, new_value):
    if file == "config":
        file = "config.json"
    elif file == "db" or file == "database":
        file = "db/db.json"

    with open(file, encoding = "utf-8") as file_:
        data = json.load(file_)

    segments = data_path.split('/')
    current_data = data

    for segment in segments[:-1]:
        current_data = current_data.setdefault(segment, {})

    current_data[segments[-1]] = new_value

    with open(file, "w") as file_:
        json.dump(data, file_, indent = 4)