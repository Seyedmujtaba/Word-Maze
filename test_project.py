import json

import pytest

from project import (
    get_random_word,
    load_word_data,
    simulate_round,
    get_progress,
    update_progress,
    reset_progress,
)


def test_load_word_data_primes_loader_and_validates_schema(tmp_path):
    words = {
        "animals": {
            "easy": ["cat", "dog"],
            "hard": ["hippopotamus"],
        }
    }
    p = tmp_path / "words.json"
    p.write_text(json.dumps(words), encoding="utf-8")

    loaded = load_word_data(str(p))
    assert loaded == words

    # invalid schemas should raise
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"animals": {"easy": []}}), encoding="utf-8")
    with pytest.raises(ValueError):
        load_word_data(str(bad))


def test_get_random_word_filters_and_is_deterministic_with_seed(tmp_path):
    words = {
        "colors": {"easy": ["red", "blue"], "hard": ["magenta"]},
        "fruits": {"easy": ["apple"], "hard": ["pomegranate"]},
    }
    p = tmp_path / "words.json"
    p.write_text(json.dumps(words), encoding="utf-8")
    load_word_data(str(p))

    w1 = get_random_word("colors", "easy", seed=1)
    w2 = get_random_word("colors", "easy", seed=1)
    assert w1 in {"red", "blue"}
    assert w2 in {"red", "blue"}

    only = get_random_word("colors", "hard", seed=99)
    assert only == "magenta"

    with pytest.raises(ValueError):
        get_random_word("does_not_exist", "easy", seed=0)


def test_simulate_round_win_and_loss():
    r = simulate_round("CAT", ["c", "a", "t"])
    assert r.won is True
    assert r.round_score > 0

    r2 = simulate_round("A", list("BCDEFGHI"))
    assert r2.won is False
    assert r2.mistakes > 0


def test_progress_update_and_reset(tmp_path):
    p = tmp_path / "save.json"

    prog = get_progress(str(p))
    assert prog["total_score"] == 0
    assert prog["games_played"] == 0

    prog2 = update_progress(40, True, path=str(p))
    assert prog2["total_score"] == 40
    assert prog2["games_played"] == 1
    assert prog2["wins"] == 1
    assert prog2["losses"] == 0

    reset_progress(str(p))
    prog3 = get_progress(str(p))
    assert prog3 == {"total_score": 0, "games_played": 0, "wins": 0, "losses": 0}
