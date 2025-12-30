from src.main import main as game_main
from src.word_loader import load_words
from src.progress_manager import ProgressManager
from src.config import Config
from src.game_state import GameState


def main():
    print("Starting Word Maze...")
    config = Config()
    words = load_words(config.WORDS_PATH)
    progress = ProgressManager(config.SAVE_PATH)
    state = GameState(words, progress)
    game_main(state)
    print("Game finished.")


def load_word_data():
    config = Config()
    words = load_words(config.WORDS_PATH)
    print(f"{len(words)} words loaded.")
    return words


def get_progress():
    config = Config()
    progress = ProgressManager(config.SAVE_PATH)
    data = progress.load_progress()
    print("Current progress:", data)
    return data


def reset_progress():
    config = Config()
    progress = ProgressManager(config.SAVE_PATH)
    progress.reset_progress()
    print("Progress has been reset.")


if __name__ == "__main__":
    main()
