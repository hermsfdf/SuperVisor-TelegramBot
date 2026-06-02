import sys
import os
import json

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)  # exe
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # python

config_path = os.path.join(BASE_DIR, "config.json")

with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

TOKEN = config["TOKEN"].strip()
ADMIN_ID = config["ADMIN_ID"]

RESTART_LIMIT = 2
RESTART_WINDOW = 300
CHECK_DELAY = 2
