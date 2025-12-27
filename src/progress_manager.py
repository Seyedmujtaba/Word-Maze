import json
import os

default = {
    "total_score": 0,
    "games_played": 0,
    "wins": 0,
    "losses": 0
}


def progress(path):
    if not os.path.exists(path):
        save_progress(path, default.copy())
        return default.copy()

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        save_progress(path, default.copy())
        return default.copy()


def save_progress(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def update(path, result):
    data = progress(path)

    data["total_score"] += result.get("round_score", 0)
    data["games_played"] += 1

    if result.get("won"):
        data["wins"] += 1
    else:
        data["losses"] += 1

    save_progress(path, data)
    return data

# when the game ended
def reset_progress(path):
    save_progress(path, default.copy())

load_progress = progress
update_progress = update
