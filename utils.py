def validate_input(name, watts, hours, unit="Hours"):
    if not name.strip():
        return False, "Name cannot be empty"
    if watts <= 0:
        return False, "Watts must be greater than 0"
    if unit == "Minutes":
        if hours <= 0 or hours > 1440:
            return False, "Minutes must be between 1 and 1440"
    else:
        if hours <= 0 or hours > 24:
            return False, "Hours must be between 1 and 24"
    return True, ""


def format_kwh(kwh, unit="kWh"):
    return f"{kwh:.2f} {unit}"


def generate_recommendation(name, kwh):
    if kwh > 200:
        return f"{name}: ⚠️ Very high usage. Consider reducing hours or replacing with energy-efficient model."
    elif kwh > 100:
        return f"{name}: ⚡ Moderate usage. Try limiting daily usage."
    else:
        return f"{name}: ✅ Low usage. Efficient appliance."


def generate_overall_insight(ranked_list):
    if not ranked_list:
        return "No data available."

    top = ranked_list[0]
    total = sum(kwh for _, kwh in ranked_list)
    percent = (top[1] / total) * 100 if total > 0 else 0

    return (
        f"\n🔍 Top Energy Consumer: {top[0]}\n"
        f"Consumes {percent:.1f}% of total energy.\n"
        f"👉 Focus on reducing usage of this appliance first."
    )