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


def migrate_scores():
    migration_data = load_scores()
    reformatted_data = {}

    for ticker, decay_score in migration_data.items():

        clean_score = float(decay_score)

        reformatted_data[ticker] = {
            "decay_score": clean_score,
            "ytd_score": clean_score,
            "delta": 0.0,
        }

    save_scores(reformatted_data)
    print("Migration complete! historical_scores.json has been upgraded.")


if __name__ == "__main__":
    migrate_scores()
