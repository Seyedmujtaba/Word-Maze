import json
import random

data = {}
used = set()


def load(file_path):
    global data, used
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    used = set()


def load_data(obj):
    global data, used
    data = obj
    used = set()


def categories():
    return list(data.keys())


def words(category=None, difficulty=None):
    result = []
    for cat in data:
        if category and cat != category:
            continue

        for diff in data[cat]:
            if difficulty and diff != difficulty:
                continue

            for w in data[cat][diff]:
                result.append(w)

    return result


def random_word(category=None, difficulty=None):
    global used

    if not data:
        raise RuntimeError()

    all_words = words(category, difficulty)
    if not all_words:
        raise ValueError()

    available = []
    for w in all_words:
        if w not in used:
            available.append(w)

    if not available:
        used.clear()
        available = all_words

    word = random.choice(available)
    used.add(word)

    return word
