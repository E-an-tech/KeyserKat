import json
import os

def load_levels():
    path = os.path.join("data", "levels.json")
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

LEVELS = load_levels()
