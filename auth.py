import json
import hashlib
import os

USERS_FILE = "users.json"


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        content = f.read().strip()
        if not content:          # ← file exists but is empty
            return {}
        return json.loads(content)


def _save_users(users: dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def register(username: str, password: str) -> tuple[bool, str]:
    """Returns (success, message)"""
    if not username or not password:
        return False, "Username and password cannot be empty."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."

    users = _load_users()
    if username in users:
        return False, "Username already exists."

    users[username] = _hash_password(password)
    _save_users(users)
    return True, "Account created successfully!"


def login(username: str, password: str) -> tuple[bool, str]:
    """Returns (success, message)"""
    if not username or not password:
        return False, "Please enter username and password."

    users = _load_users()
    if username not in users:
        return False, "Invalid username or password."
    if users[username] != _hash_password(password):
        return False, "Invalid username or password."

    return True, f"Welcome, {username}!"