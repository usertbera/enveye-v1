import json
from pathlib import Path

CONFIG_FILE = Path(__file__).resolve().parent.parent / "config.json"

def load_config():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"⚠️ config.json not found at {CONFIG_FILE}")
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

# Expose as CONFIG
CONFIG = load_config()
