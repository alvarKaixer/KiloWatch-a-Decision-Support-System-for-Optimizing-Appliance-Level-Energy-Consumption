import json, os, datetime

_SAVE_FILE    = "kilowatch_data.json"
_HISTORY_FILE = "kilowatch_history.json"

def save_appliances(data: dict):
    with open(_SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_appliances() -> dict:
    if not os.path.exists(_SAVE_FILE):
        return {}
    try:
        with open(_SAVE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_history(history: list):
    serialisable = []
    for rpt in history:
        serialisable.append({
            "timestamp": rpt["timestamp"],
            "label":     rpt.get("label", ""),
            "ranked":    rpt["ranked"],
        })
    with open(_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(serialisable, f, indent=2)

def load_history() -> list:
    if not os.path.exists(_HISTORY_FILE):
        return []
    try:
        with open(_HISTORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []