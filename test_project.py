from project import load_word_data, get_progress, reset_progress


def test_load_word_data():
    words = load_word_data()
    assert type(words) is list
    assert len(words) > 0


def test_get_progress():
    progress = get_progress()
    assert type(progress) is dict


def test_reset_progress():
    reset_progress()
    progress = get_progress()
    assert type(progress) is dict
