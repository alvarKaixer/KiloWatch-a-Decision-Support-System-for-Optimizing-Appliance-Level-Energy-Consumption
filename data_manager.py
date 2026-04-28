import json
import os

FILE = "data.json"

def load_data():
    if not os.path.exists(FILE):
        return {}
    with open(FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_appliance(name, watts, hours):
    data = load_data()
    data[name] = {
        "watts": watts,
        "hours": hours
    }
    save_data(data)

def remove_appliance(name):
    data = load_data()
    if name in data:
        del data[name]
        save_data(data)

def get_all():
    return load_data()