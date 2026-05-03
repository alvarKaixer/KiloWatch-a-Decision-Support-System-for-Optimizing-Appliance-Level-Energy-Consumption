def compute_kwh(watts, hours, frequency=1.0):
    # daily kWh × frequency multiplier for realistic monthly estimate
    daily_kwh = (watts * hours) / 1000
    return daily_kwh * frequency

def compute_all(data):
    results = []
    for name, info in data.items():
        freq = info.get("frequency", 1.0)
        kwh  = compute_kwh(info["watts"], info["hours"], freq)
        results.append((name, kwh))
    return results

def rank_appliances(results):
    return sorted(results, key=lambda x: x[1], reverse=True)