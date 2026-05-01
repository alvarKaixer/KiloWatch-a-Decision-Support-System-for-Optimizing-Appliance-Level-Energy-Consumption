import json, os, datetime

def _save_file(username):
    return f"kilowatch_data_{username}.json"

def _history_file(username):
    return f"kilowatch_history_{username}.json"

def save_appliances(data: dict, username: str = "User"):
    with open(_save_file(username), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_appliances(username: str = "User") -> dict:
    path = _save_file(username)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_history(history: list, username: str = "User"):
    serialisable = []
    for rpt in history:
        serialisable.append({
            "timestamp": rpt["timestamp"],
            "label":     rpt.get("label", ""),
            "ranked":    rpt["ranked"],
        })
    with open(_history_file(username), "w", encoding="utf-8") as f:
        json.dump(serialisable, f, indent=2)

def load_history(username: str = "User") -> list:
    path = _history_file(username)
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []