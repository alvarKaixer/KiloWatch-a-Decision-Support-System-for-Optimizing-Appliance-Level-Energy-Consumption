_appliances = {}

def add_appliance(name, watts, hours):
    _appliances[name] = {"watts": watts, "hours": hours}

def remove_appliance(name):
    _appliances.pop(name, None)

def get_all():
    return _appliances

def clear_all():
    _appliances.clear()