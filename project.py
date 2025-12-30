from src.word_loader import load_word_list
from src.progress_manager import ProgressManager
from src.config import Config


def main():
    config = Config()
    words = load_word_list(config.WORDS_PATH)
    progress = ProgressManager(config.SAVE_PATH)
    progress.load_progress()
    return words


def load_word_data():
    config = Config()
    return load_word_list(config.WORDS_PATH)


def get_progress():
    config = Config()
    progress = ProgressManager(config.SAVE_PATH)
    return progress.load_progress()


def reset_progress():
    config = Config()
    progress = ProgressManager(config.SAVE_PATH)
    progress.reset_progress()
