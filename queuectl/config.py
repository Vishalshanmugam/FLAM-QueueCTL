import json
import os

CONFIG_FILE = os.path.expanduser("~/.queuectl_config.json")

DEFAULT_CONFIG = {
    "max_retries": 3,
    "backoff_base": 2
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

def set_value(key, value):
    cfg = load_config()
    cfg[key] = int(value) if value.isdigit() else value
    save_config(cfg)
    print(f"Config updated: {key} = {cfg[key]}")

