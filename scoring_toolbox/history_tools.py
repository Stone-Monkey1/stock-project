import json
import os

SCORE_FILE = "historical_scores.json"


def load_scores():
    """Loads the historical scores from the JSON file. Returns an empty dictionary if it doesn't exist."""
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, "r") as file:
            return json.load(file)
    return {}  # Return an empty dictionary the very first time you run the script


def save_scores(score_dict):
    """Saves the updated score dictionary back to the JSON file."""
    with open(SCORE_FILE, "w") as file:
        json.dump(score_dict, file, indent=4)
