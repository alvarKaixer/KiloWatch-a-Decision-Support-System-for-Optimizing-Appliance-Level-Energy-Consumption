_appliances = {}

def add_appliance(name, watts, hours, frequency=1.0):
    _appliances[name] = {"watts": watts, "hours": hours, "frequency": frequency}

def remove_appliance(name):
    _appliances.pop(name, None)

def get_all():
    return _appliances

def clear_all():
    _appliances.clear()