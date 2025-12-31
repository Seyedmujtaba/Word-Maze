"""Word Maze (CS50P-style entry point).

This repository is primarily a PyQt5 desktop game (see `src/main.py`).

For automated testing (pytest) we keep **all GUI imports lazy**, so importing
this module does not require a graphical environment.

The functions below provide a small, testable API around the project's core
non-GUI modules:
  - src/word_loader.py
  - src/game_state.py
  - src/progress_manager.py
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
import random
from typing import Any, Dict, Iterable, Optional

from src.game_state import GameState
from src import word_loader
from src import progress_manager


def repo_root() -> str:
    """Return absolute path to repository root (directory containing project.py)."""
    return os.path.dirname(os.path.abspath(__file__))


def data_path(*parts: str) -> str:
    """Build an absolute path inside the repo's data/ directory."""
    return os.path.join(repo_root(), "data", *parts)


def words_file() -> str:
    """Default path to the words dataset used by the game."""
    return data_path("words.json")


def progress_file() -> str:
    """Default path to the progress save file used by the game."""
    return data_path("save_data.json")


def _validate_words_schema(data: Any) -> Dict[str, Dict[str, list]]:
    """Validate the expected schema of words.json.

    Expected:
        {category: {difficulty: [word, ...], ...}, ...}
    """
    if not isinstance(data, dict) or not data:
        raise ValueError("words data must be a non-empty dict")

    for category, by_diff in data.items():
        if not isinstance(category, str) or not category:
            raise ValueError("category names must be non-empty strings")
        if not isinstance(by_diff, dict) or not by_diff:
            raise ValueError("each category must map to a non-empty dict")
        for diff, words in by_diff.items():
            if not isinstance(diff, str) or not diff:
                raise ValueError("difficulty names must be non-empty strings")
            if not isinstance(words, list) or not words:
                raise ValueError("each difficulty must map to a non-empty list")
            if not all(isinstance(w, str) and w for w in words):
                raise ValueError("all words must be non-empty strings")

    return data  # type: ignore[return-value]


def load_word_data(file_path: Optional[str] = None) -> Dict[str, Dict[str, list]]:
    """Load words data from JSON and prime src.word_loader.

    Args:
        file_path: Optional override (useful for tests).

    Returns:
        The parsed JSON object.
    """
    path = file_path or words_file()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    data = _validate_words_schema(data)
    word_loader.load_data(data)
    return data


def get_categories(file_path: Optional[str] = None) -> list[str]:
    """Return available categories. Loads the dataset first if needed."""
    if not word_loader.data:
        load_word_data(file_path)
    return word_loader.categories()


def get_random_word(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    *,
    seed: Optional[int] = None,
    file_path: Optional[str] = None,
) -> str:
    """Pick a random word, optionally filtered by category/difficulty.

    Mirrors src.word_loader.random_word behavior (no immediate repeats)
    via word_loader.used.
    """
    if not word_loader.data:
        load_word_data(file_path)

    all_words = word_loader.words(category, difficulty)
    if not all_words:
        raise ValueError("no words match the given filters")

    available = [w for w in all_words if w not in word_loader.used]
    if not available:
        word_loader.used.clear()
        available = list(all_words)

    rng = random.Random(seed) if seed is not None else random
    word = rng.choice(available)
    word_loader.used.add(word)
    return word


@dataclass(frozen=True)
class RoundResult:
    """Typed container around GameState.finish_round() output."""

    round_score: int
    won: bool
    bonus: int
    mistakes: int


def simulate_round(word: str, guesses: Iterable[str], *, use_hint: bool = False) -> RoundResult:
    """Play a round in memory (no UI) and return the final result."""
    state = GameState(word)

    used_hint = False
    for g in guesses:
        if state.is_won() or state.is_lost():
            break

        payload = state.guess(str(g))

        if use_hint and (not used_hint) and payload.get("correct") and not state.hint_used:
            state.use_hint()
            used_hint = True

    result = state.finish_round()
    return RoundResult(
        round_score=int(result.get("round_score", 0)),
        won=bool(result.get("won")),
        bonus=int(result.get("bonus", 0)),
        mistakes=int(result.get("mistakes", 0)),
    )


def get_progress(path: Optional[str] = None) -> dict:
    """Load progress dict (creates a default file if missing)."""
    p = path or progress_file()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return progress_manager.load_progress(p)


def update_progress(round_score: int, won: bool, *, path: Optional[str] = None) -> dict:
    """Update progress with a finished round result and return the updated dict."""
    if not isinstance(round_score, int):
        raise TypeError("round_score must be int")

    p = path or progress_file()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return progress_manager.update_progress(p, {"round_score": round_score, "won": bool(won)})


def reset_progress(path: Optional[str] = None) -> None:
    """Reset progress back to defaults."""
    p = path or progress_file()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    progress_manager.reset_progress(p)


def main() -> None:
    """Launch the PyQt5 game UI (lazy import so tests don't need PyQt5)."""
    from src.main import main as gui_main  # lazy import (PyQt5)
    gui_main()


if __name__ == "__main__":
    main()
