def compute_kwh(watts, hours):
    # daily kWh
    return (watts * hours) / 1000

def compute_all(data):
    results = []

    for name, info in data.items():
        kwh = compute_kwh(info["watts"], info["hours"])
        results.append((name, kwh))

    return results

def rank_appliances(results):
    return sorted(results, key=lambda x: x[1], reverse=True)