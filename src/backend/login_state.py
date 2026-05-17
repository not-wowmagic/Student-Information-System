
import json
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_FOLDER = os.path.join(PROJECT_ROOT, "data")
LOGIN_FILE = os.path.join(DATA_FOLDER, "login_credentials.json")


def load_login_credentials():
    if not os.path.exists(LOGIN_FILE):
        return {}

    try:
        with open(LOGIN_FILE, "r") as file:
            return json.load(file)
    except:
        return {}


def save_login_credentials(username, password=None):
    os.makedirs(DATA_FOLDER, exist_ok=True)

    credentials = {
        "username": username,
    }

    with open(LOGIN_FILE, "w") as file:
        json.dump(credentials, file, indent=2)


