import sys
import random
import string
from typing import Dict, List, Set, Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QStackedWidget, QFrame,
    QComboBox, QButtonGroup, QRadioButton, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from BlurWindow.blurWindow import GlobalBlur  
GAME_CONFIG = {
    "resolution": (1280, 720),  
    "colors": {
        "primary": "#1A73E8",
        "accent": "#FACC15",
        "text": "#FFFFFF",
        "glass_bg": "rgba(255, 255, 255, 0.08)",
        "glass_border": "rgba(255, 255, 255, 0.35)",
        "life_full": "rgba(255, 255, 255, 0.95)",
        "life_empty": "rgba(255, 255, 255, 0.20)"
    },
    "fonts": {
        "family": "Segoe UI",
    }
}

WORD_DB = {
    "Animals": ["ELEPHANT", "GIRAFFE", "DOLPHIN", "KANGAROO",
                "PENGUIN", "CHEETAH", "TIGER", "LION"],
    "Fruits": ["STRAWBERRY", "PINEAPPLE", "BLUEBERRY", "WATERMELON", "APRICOT"],
    "Colors": ["TURQUOISE", "LAVENDER", "CRIMSON", "EMERALD", "MAGENTA", "INDIGO"]
}

# --- Global scaling helpers (responsive UI) ---
BASE_WIDTH = 1280.0
BASE_HEIGHT = 720.0
UI_SCALE = 1.0 


def S(x: float) -> int:
    """Scale for sizes (pixels) based on screen width."""
    return int(x * UI_SCALE)


def F(x: float) -> int:
    """Scale for font sizes."""
    v = int(x * UI_SCALE)
    return max(v, 1)


def clear_layout(layout) -> None:
    """Remove and detach all widgets (and nested layouts) from a layout."""
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w is not None:
            w.setParent(None)
            continue
        sub = item.layout()
        if sub is not None:
            clear_layout(sub)


# --- Style Sheet (Glassmorphism) ---
STYLESHEET = """
QMainWindow {
    background: transparent; /* Blur واقعی توسط ویندوز اعمال می‌شود */
}

/* Default labels */
QLabel {
    color: #F9FAFB;
    font-family: 'Segoe UI', sans-serif;
}

/* Glass Card Style */
QFrame#GlassCard {
    background-color: rgba(15, 23, 42, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.35);
    border-radius: 26px;
}

/* Buttons base */
QPushButton {
    border-radius: 20px;
    padding: 10px 18px;
    font-weight: 600;
    font-size: 14px;
    font-family: 'Segoe UI', sans-serif;
}

/* Primary (blue) */
QPushButton#PrimaryButton {
    background-color: #1A73E8;
    color: white;
    border: none;
}
QPushButton#PrimaryButton:hover {
    background-color: #1557B0;
}

/* Secondary (yellow) - Hint button */
QPushButton#SecondaryButton {
    background-color: #FACC15;
    color: #111827;
    border: none;
    border-radius: 24px;
    padding: 10px 22px;
}
QPushButton#SecondaryButton:hover {
    background-color: #EAB308;
}

/* Ghost (outline) */
QPushButton#GhostButton {
    background-color: transparent;
    color: #F9FAFB;
    border: 1px solid rgba(249, 250, 251, 0.5);
}
QPushButton#GhostButton:hover {
    background-color: rgba(15, 23, 42, 0.6);
}

/* Keyboard buttons */
QPushButton#KeyButton {
    background-color: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.18);
    color: #E5E7EB;
    border-radius: 16px;
}
QPushButton#KeyButton:hover {
    background-color: rgba(248, 250, 252, 0.18);
}
QPushButton#KeyButton:disabled {
    border: 1px solid rgba(148, 163, 184, 0.2);
}

/* Exit button (top-right) */
QPushButton#ExitButton {
    background-color: rgba(15, 23, 42, 0.85);
    color: #F9FAFB;
    border-radius: 20px;
    border: 1px solid rgba(248, 250, 252, 0.5);
    font-size: 16px;
    font-weight: 700;
}
QPushButton#ExitButton:hover {
    background-color: rgba(239, 68, 68, 0.9);
}

/* ComboBox */
QComboBox {
    background-color: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.6);
    border-radius: 10px;
    color: #E5E7EB;
    padding: 6px 10px;
    font-size: 13px;
}
QComboBox QAbstractItemView {
    background-color: #020617;
    color: #F9FAFB;
    selection-background-color: #1A73E8;
}

/* Letter Slot (underscore boxes) */
QLabel#LetterSlot {
    background-color: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(248, 250, 252, 0.5);
    border-radius: 22px;
    color: #E5E7EB;
    font-size: 24px;
    font-weight: 600;
}

/* Preview text (----- under Game Info) */
QLabel#PreviewLabel {
    color: #E5E7EB;
    font-family: 'Consolas', monospace;
}

/* Little status label */
QLabel#StatusMessage {
    color: rgba(248, 250, 252, 0.75);
    font-size: 13px;
}

/* --- Menu Redesign --- */
QFrame#MenuCard {
    background-color: rgba(15, 23, 42, 0.60);
    border: 1px solid rgba(255, 255, 255, 0.30);
    border-radius: 30px;
}
QLabel#MenuSubtitle {
    color: rgba(248, 250, 252, 0.72);
}
QLabel#MenuFieldLabel {
    color: rgba(248, 250, 252, 0.82);
}
QLabel#MenuFooter {
    color: rgba(248, 250, 252, 0.55);
}
QPushButton#PillButton {
    background-color: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(148, 163, 184, 0.45);
    color: rgba(248, 250, 252, 0.92);
    border-radius: 18px;
    padding: 8px 14px;
}
QPushButton#PillButton:hover {
    background-color: rgba(248, 250, 252, 0.12);
}
QPushButton#PillButton:checked {
    background-color: rgba(26, 115, 232, 0.95);
    border: 1px solid rgba(26, 115, 232, 1.0);
    color: #FFFFFF;
}
"""


# --- Custom Widgets ---

class GlassCard(QFrame):
    """A container with glassmorphism styling."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("GlassCard")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(S(40))
        shadow.setColor(QColor(0, 0, 0, 200))
        shadow.setOffset(0, S(18))
        self.setGraphicsEffect(shadow)


# --- Screens ---

class MainMenuScreen(QWidget):
    start_game_signal = pyqtSignal(str, str)  # Category, Difficulty

    def __init__(self):
        super().__init__()
        self._STYLE_SLOT_REVEALED = (
            "background-color: rgba(248, 250, 252, 0.9);"
            "color: #020617;"
            "border-radius: 30px;"
            f"font-weight: 800; font-size: {F(30)}px;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(S(60), S(50), S(60), S(50))
        outer.setSpacing(S(20))

        outer.addStretch()

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.addStretch()

        menu_card = GlassCard()
        menu_card.setObjectName("MenuCard")
        menu_card.setFixedWidth(S(860))

        card_layout = QVBoxLayout(menu_card)
        card_layout.setContentsMargins(S(56), S(50), S(56), S(46))
        card_layout.setSpacing(S(18))

        title = QLabel("Word-Maze")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont(GAME_CONFIG['fonts']['family'], F(48), QFont.Bold))

        subtitle = QLabel("Guess the word. Beat the maze.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setObjectName("MenuSubtitle")
        subtitle.setFont(QFont(GAME_CONFIG['fonts']['family'], F(14)))

        divider = QFrame()
        divider.setFixedHeight(S(1))
        divider.setStyleSheet("background-color: rgba(248, 250, 252, 0.16); border: none;")

        # Form area (2 columns: Category / Difficulty)
        form = QWidget()
        form_layout = QGridLayout(form)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setHorizontalSpacing(S(18))
        form_layout.setVerticalSpacing(S(10))

        label_cat = QLabel("Category")
        label_cat.setObjectName("MenuFieldLabel")
        label_cat.setFont(QFont(GAME_CONFIG['fonts']['family'], F(13), QFont.DemiBold))

        self.category_combo = QComboBox()
        self.category_combo.addItems(WORD_DB.keys())
        self.category_combo.setFixedHeight(S(44))
        self.category_combo.setStyleSheet(f"font-size: {F(14)}px;")

        label_diff = QLabel("Difficulty")
        label_diff.setObjectName("MenuFieldLabel")
        label_diff.setFont(QFont(GAME_CONFIG['fonts']['family'], F(13), QFont.DemiBold))

        diff_container = QWidget()
        diff_layout = QHBoxLayout(diff_container)
        diff_layout.setContentsMargins(0, 0, 0, 0)
        diff_layout.setSpacing(S(10))

        self.diff_group = QButtonGroup(self)
        self.diff_group.setExclusive(True)

        modes = ["Easy", "Medium", "Hard"]
        self._diff_buttons: List[QPushButton] = []
        for mode in modes:
            b = QPushButton(mode)
            b.setObjectName("PillButton")
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.setFixedHeight(S(44))
            b.setStyleSheet(f"font-size: {F(14)}px;")
            self.diff_group.addButton(b)
            diff_layout.addWidget(b)
            self._diff_buttons.append(b)

        # Default: Medium
        if len(self._diff_buttons) >= 2:
            self._diff_buttons[1].setChecked(True)

        form_layout.addWidget(label_cat, 0, 0)
        form_layout.addWidget(label_diff, 0, 1)
        form_layout.addWidget(self.category_combo, 1, 0)
        form_layout.addWidget(diff_container, 1, 1)
        form_layout.setColumnStretch(0, 1)
        form_layout.setColumnStretch(1, 1)

        # Actions
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(S(12))

        self.btn_play = QPushButton("Play")
        self.btn_play.setObjectName("PrimaryButton")
        self.btn_play.setFixedHeight(S(54))
        self.btn_play.setCursor(Qt.PointingHandCursor)
        self.btn_play.setStyleSheet(f"font-size: {F(16)}px;")
        self.btn_play.clicked.connect(self.on_play)

        self.btn_quit = QPushButton("Quit")
        self.btn_quit.setObjectName("GhostButton")
        self.btn_quit.setFixedHeight(S(54))
        self.btn_quit.setCursor(Qt.PointingHandCursor)
        self.btn_quit.setStyleSheet(f"font-size: {F(16)}px;")
        self.btn_quit.clicked.connect(QApplication.instance().quit)

        actions_layout.addWidget(self.btn_play, 1)
        actions_layout.addWidget(self.btn_quit, 1)

        footer = QLabel("Created by: Seyedmujtaba Tabatabaee & Ayla Rasouli")
        footer.setAlignment(Qt.AlignCenter)
        footer.setObjectName("MenuFooter")
        footer.setFont(QFont(GAME_CONFIG['fonts']['family'], F(11)))

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(S(8))
        card_layout.addWidget(divider)
        card_layout.addSpacing(S(8))
        card_layout.addWidget(form)
        card_layout.addSpacing(S(14))
        card_layout.addLayout(actions_layout)
        card_layout.addSpacing(S(14))
        card_layout.addWidget(footer)

        row.addWidget(menu_card)
        row.addStretch()

        outer.addLayout(row)
        outer.addStretch()

    def on_play(self):
        cat = self.category_combo.currentText()
        diff_btn = self.diff_group.checkedButton()
        diff = diff_btn.text() if diff_btn is not None else "Medium"
        self.start_game_signal.emit(cat, diff)


class GameScreen(QWidget):
    game_over_signal = pyqtSignal(bool, str, int)  # Win/Lose, Word, Score

    _STYLE_KEY_CORRECT = (
        "background-color: rgba(191, 219, 254, 0.95);"
        "color: #020617; border-radius: 20px; font-weight: 700;"
    )
    _STYLE_KEY_WRONG = (
        "background-color: rgba(239, 68, 68, 0.9);"
        "color: white; border-radius: 20px; font-weight: 700;"
    )
    _STYLE_SLOT_REVEALED = (
        "background-color: rgba(248, 250, 252, 0.9);"
        "color: #020617;"
        "border-radius: 30px;"
        "font-weight: 600; font-size: 32px;"
    )

    def __init__(self):
        super().__init__()
        self.current_word: str = ""
        self._current_word_set: Set[str] = set()

        self.guesses: Set[str] = set()
        self.lives: int = 8
        self.score: int = 0
        self.max_lives: int = 8

        self.key_buttons: Dict[str, QPushButton] = {}
        self.slot_labels: List[QLabel] = []
        self.life_dots: List[QLabel] = []

        self.category: str = ""
        self.difficulty: str = ""

        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(S(40), S(40), S(40), S(40))
        main_layout.setSpacing(S(26))

        # LEFT: Game Info
        left_card = GlassCard()
        left_card.setFixedWidth(S(420))
        left_layout = QVBoxLayout(left_card)

        self.lbl_info_title = QLabel("Game Info")
        self.lbl_info_title.setFont(QFont(GAME_CONFIG['fonts']['family'], F(24), QFont.Bold))
        self.lbl_info_title.setAlignment(Qt.AlignLeft)

        self.lbl_cat = QLabel("Category: –")
        self.lbl_diff = QLabel("Difficulty: –")

        self.lbl_preview = QLabel("_ _ _ _ _")
        self.lbl_preview.setObjectName("PreviewLabel")
        self.lbl_preview.setFont(QFont("Consolas", F(26)))
        self.lbl_preview.setAlignment(Qt.AlignLeft)
        self.lbl_preview.setStyleSheet("margin-top: 40px; margin-bottom: 8px;")

        self.lbl_wrong = QLabel("Wrong: ")
        self.lbl_wrong.setWordWrap(True)
        self.lbl_wrong.setStyleSheet("color: rgba(248,248,255,0.7); font-size: 13px;")

        self.lbl_score = QLabel("Score: 0")
        self.lbl_score.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 20px;")

        left_layout.addWidget(self.lbl_info_title)
        left_layout.addSpacing(S(20))
        left_layout.addWidget(self.lbl_cat)
        left_layout.addWidget(self.lbl_diff)
        left_layout.addSpacing(S(30))
        left_layout.addWidget(self.lbl_preview)
        left_layout.addWidget(self.lbl_wrong)
        left_layout.addStretch()
        left_layout.addWidget(self.lbl_score)
        left_layout.setContentsMargins(S(30), S(30), S(30), S(30))

        # RIGHT: Main gameplay
        right_layout = QVBoxLayout()
        right_layout.setSpacing(S(20))

        # Status card
        status_card = GlassCard()
        status_layout = QVBoxLayout(status_card)
        self.lbl_status_title = QLabel("Guess The Word")
        self.lbl_status_title.setFont(QFont(GAME_CONFIG['fonts']['family'], F(30), QFont.Bold))
        self.lbl_status_title.setAlignment(Qt.AlignCenter)

        self.lbl_msg = QLabel("Pick a letter to begin")
        self.lbl_msg.setObjectName("StatusMessage")
        self.lbl_msg.setAlignment(Qt.AlignCenter)

        status_layout.addSpacing(S(10))
        status_layout.addWidget(self.lbl_status_title)
        status_layout.addWidget(self.lbl_msg)
        status_layout.addSpacing(S(10))

        # Word slots
        self.slots_container = QWidget()
        self.slots_layout = QHBoxLayout(self.slots_container)
        self.slots_layout.setAlignment(Qt.AlignCenter)
        self.slots_layout.setSpacing(S(12))

        # Lives row
        self.lives_container = QWidget()
        self.lives_layout = QHBoxLayout(self.lives_container)
        self.lives_layout.setAlignment(Qt.AlignCenter)
        self.lives_layout.setSpacing(S(10))
        self._build_lives_ui()

        # Keyboard (QWERTY layout)
        keyboard_card = GlassCard()
        keyboard_layout = QGridLayout(keyboard_card)
        keyboard_layout.setSpacing(S(12))

        rows = [
            "QWERTYUIOP",
            "ASDFGHJKL",
            "ZXCVBNM"
        ]

        start_cols = [0, 1, 2]

        key_font = QFont(GAME_CONFIG['fonts']['family'], F(30), QFont.Bold)

        for r, letters_row in enumerate(rows):
            c0 = start_cols[r]
            for i, letter in enumerate(letters_row):
                btn = QPushButton(letter)
                btn.setObjectName("KeyButton")
                btn.setFixedSize(S(70), S(70))
                btn.setFont(key_font)
                btn.setStyleSheet(f"font-size: {F(30)}px; font-weight: 800;")
                btn.setCursor(Qt.PointingHandCursor)
                btn.clicked.connect(lambda checked, l=letter: self.make_guess(l))

                keyboard_layout.addWidget(btn, r, c0 + i)
                self.key_buttons[letter] = btn

        # Bottom controls
        bottom_layout = QHBoxLayout()
        self.btn_hint = QPushButton("Hint")
        self.btn_hint.setObjectName("SecondaryButton")
        self.btn_hint.setFixedWidth(S(130))
        self.btn_hint.clicked.connect(self.use_hint)
        self.btn_hint.setCursor(Qt.PointingHandCursor)

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setObjectName("GhostButton")
        self.btn_reset.setFixedWidth(S(130))
        self.btn_reset.clicked.connect(self.reset_round)
        self.btn_reset.setCursor(Qt.PointingHandCursor)

        bottom_layout.addWidget(self.btn_hint)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_reset)

        right_layout.addWidget(status_card)
        right_layout.addWidget(self.slots_container)
        right_layout.addWidget(self.lives_container)
        right_layout.addWidget(keyboard_card)
        right_layout.addLayout(bottom_layout)

        main_layout.addWidget(left_card)
        main_layout.addLayout(right_layout)

    def _build_lives_ui(self) -> None:
        """Create life dots once; later we only update their styles."""
        clear_layout(self.lives_layout)
        self.life_dots.clear()

        size = S(20)
        for _ in range(self.max_lives):
            dot = QLabel()
            dot.setFixedSize(size, size)
            self.life_dots.append(dot)
            self.lives_layout.addWidget(dot)

    def _ensure_slots_built(self) -> None:
        """Rebuild slot labels only if needed (e.g., new word length)."""
        if len(self.slot_labels) == len(self.current_word) and self.slot_labels:
            return

        clear_layout(self.slots_layout)
        self.slot_labels.clear()

        for _ in self.current_word:
            lbl = QLabel("_")
            lbl.setObjectName("LetterSlot")
            lbl.setFixedSize(S(90), S(90))
            lbl.setAlignment(Qt.AlignCenter)
            self.slot_labels.append(lbl)
            self.slots_layout.addWidget(lbl)

    def setup_game(self, category: str, difficulty: str) -> None:
        self.category = category
        self.difficulty = difficulty
        self.lbl_cat.setText(f"Category: {category}")
        self.lbl_diff.setText(f"Difficulty: {difficulty}")

        self.current_word = random.choice(WORD_DB[category])
        self._current_word_set = set(self.current_word)

        self.reset_round()

    def reset_round(self) -> None:
        self.guesses.clear()
        self.lives = self.max_lives
        self.score = 0

        self.lbl_msg.setText("Pick a letter to begin")
        self.lbl_wrong.setText("Wrong:")
        self.lbl_score.setText(f"Score: {self.score}")

        for btn in self.key_buttons.values():
            btn.setEnabled(True)
            btn.setStyleSheet(f"font-size: {F(30)}px; font-weight: 800;")

        self._update_slots_ui()
        self._update_lives_ui()
        self.update_preview()

    def _update_slots_ui(self) -> None:
        self._ensure_slots_built()

        # Update each slot label based on guesses
        for idx, char in enumerate(self.current_word):
            lbl = self.slot_labels[idx]
            if char in self.guesses:
                lbl.setText(char)
                lbl.setStyleSheet(self._STYLE_SLOT_REVEALED)
            else:
                lbl.setText("_")
                lbl.setStyleSheet("")  # back to app stylesheet (LetterSlot)

    def _update_lives_ui(self) -> None:
        size = S(20)
        for i, dot in enumerate(self.life_dots):
            color = (
                GAME_CONFIG['colors']['life_full']
                if i < self.lives
                else GAME_CONFIG['colors']['life_empty']
            )
            dot.setStyleSheet(f"background-color: {color}; border-radius: {size//2}px;")

    def update_preview(self) -> None:
        display = [c if c in self.guesses else "_" for c in self.current_word]
        self.lbl_preview.setText(" ".join(display))

        wrong_guesses = sorted([c for c in self.guesses if c not in self._current_word_set])
        self.lbl_wrong.setText("Wrong: " + ", ".join(wrong_guesses))

    def make_guess(self, letter: str) -> None:
        if letter in self.guesses:
            return

        self.guesses.add(letter)

        btn = self.key_buttons[letter]
        btn.setDisabled(True)

        if letter in self._current_word_set:
            self.score += 10
            self.lbl_msg.setText(f"Nice! {letter} is in the word.")
            btn.setStyleSheet(self._STYLE_KEY_CORRECT + f" font-size: {F(30)}px;")
        else:
            self.lives -= 1
            self.score = max(0, self.score - 5)
            self.lbl_msg.setText(f"Oops! {letter} is not in the word.")
            btn.setStyleSheet(self._STYLE_KEY_WRONG + f" font-size: {F(30)}px;")

        self.lbl_score.setText(f"Score: {self.score}")
        self._update_slots_ui()
        self._update_lives_ui()
        self.update_preview()
        self.check_win_loss()

    def use_hint(self) -> None:
        if self.score < 20:
            self.lbl_msg.setText("Not enough points for a hint!")
            return

        # IMPORTANT: keep original behavior: duplicates in word increase hint probability
        unguessed = [c for c in self.current_word if c not in self.guesses]
        if not unguessed:
            return

        self.score -= 20
        self.lbl_score.setText(f"Score: {self.score}")

        reveal = random.choice(unguessed)
        self.make_guess(reveal)

    def check_win_loss(self) -> None:
        if all(c in self.guesses for c in self.current_word):
            self.game_over_signal.emit(True, self.current_word, self.score)
        elif self.lives <= 0:
            self.game_over_signal.emit(False, self.current_word, self.score)


class ResultScreen(QWidget):
    action_signal = pyqtSignal(str)  # "menu" or "replay"

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        card = GlassCard()
        card.setFixedSize(S(420), S(320))
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)

        self.lbl_title = QLabel("You Win!")
        self.lbl_title.setFont(QFont(GAME_CONFIG['fonts']['family'], F(28), QFont.Bold))
        self.lbl_title.setAlignment(Qt.AlignCenter)

        self.lbl_word = QLabel("The word was: XXXX")
        self.lbl_word.setStyleSheet("font-size: 18px; margin-top: 10px;")

        self.lbl_final_score = QLabel("Final Score: 0")
        self.lbl_final_score.setStyleSheet("font-size: 16px; color: rgba(248,248,255,0.8);")

        btn_layout = QHBoxLayout()
        btn_replay = QPushButton("Play Again")
        btn_replay.setObjectName("PrimaryButton")
        btn_replay.clicked.connect(lambda: self.action_signal.emit("replay"))

        btn_menu = QPushButton("Back to Menu")
        btn_menu.setObjectName("GhostButton")
        btn_menu.clicked.connect(lambda: self.action_signal.emit("menu"))

        btn_layout.addWidget(btn_replay)
        btn_layout.addWidget(btn_menu)

        card_layout.addStretch()
        card_layout.addWidget(self.lbl_title)
        card_layout.addWidget(self.lbl_word)
        card_layout.addWidget(self.lbl_final_score)
        card_layout.addStretch()
        card_layout.addLayout(btn_layout)
        card_layout.addStretch()

        layout.addWidget(card)

    def set_result(self, win: bool, word: str, score: int) -> None:
        if win:
            self.lbl_title.setText("You Win!")
            self.lbl_title.setStyleSheet(
                "color: #4ADE80; font-size: 32px; font-weight: bold;"
            )
        else:
            self.lbl_title.setText("Game Over")
            self.lbl_title.setStyleSheet(
                "color: #EF4444; font-size: 32px; font-weight: bold;"
            )

        self.lbl_word.setText(f"The word was: {word}")
        self.lbl_final_score.setText(f"Final Score: {score}")


class WordMazeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Word-Maze")
        self.resize(*GAME_CONFIG["resolution"])

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.menu_screen = MainMenuScreen()
        self.game_screen = GameScreen()
        self.result_screen = ResultScreen()

        self.stack.addWidget(self.menu_screen)
        self.stack.addWidget(self.game_screen)
        self.stack.addWidget(self.result_screen)

        self.menu_screen.start_game_signal.connect(self.start_game)
        self.game_screen.game_over_signal.connect(self.show_result)
        self.result_screen.action_signal.connect(self.handle_result_action)

        self.exit_btn = QPushButton("✕", self)
        self.exit_btn.setObjectName("ExitButton")
        self.exit_btn.setFixedSize(S(40), S(40))
        self.exit_btn.clicked.connect(QApplication.instance().quit)
        self.exit_btn.setCursor(Qt.PointingHandCursor)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        margin = S(20)
        self.exit_btn.move(self.width() - self.exit_btn.width() - margin, margin)

    def start_game(self, category: str, difficulty: str) -> None:
        self.game_screen.setup_game(category, difficulty)
        self.stack.setCurrentIndex(1)
        self.showFullScreen()

    def show_result(self, win: bool, word: str, score: int) -> None:
        self.result_screen.set_result(win, word, score)
        self.stack.setCurrentIndex(2)

    def handle_result_action(self, action: str) -> None:
        if action == "replay":
            cat = self.game_screen.category
            diff = self.game_screen.difficulty
            self.start_game(cat, diff)
        else:
            self.stack.setCurrentIndex(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    screen = app.primaryScreen()
    size = screen.size()
    screen_w = size.width()
    screen_h = size.height()

    GAME_CONFIG["resolution"] = (screen_w, screen_h)

    BASE_MARGIN = 40
    BASE_MAIN_SPACING = 26
    BASE_LEFT_CARD_W = 420

    BASE_KEY_SIZE = 70
    BASE_KEY_SPACING = 12
    KEY_COLS = 10
    base_keyboard_w = KEY_COLS * BASE_KEY_SIZE + (KEY_COLS - 1) * BASE_KEY_SPACING

    BASE_SLOT_SIZE = 90
    BASE_SLOT_SPACING = 12
    max_word_len = max(len(w) for ws in WORD_DB.values() for w in ws)
    base_slots_w = max_word_len * BASE_SLOT_SIZE + (max_word_len - 1) * BASE_SLOT_SPACING

    base_right_min_w = max(base_keyboard_w, base_slots_w)

    BASE_REQUIRED_W = (2 * BASE_MARGIN) + BASE_MAIN_SPACING + BASE_LEFT_CARD_W + base_right_min_w

    UI_SCALE = min(screen_w / BASE_REQUIRED_W, screen_h / BASE_HEIGHT)

    base_font = QFont(GAME_CONFIG['fonts']['family'], F(12))
    base_font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(base_font)

    app.setStyleSheet(STYLESHEET)

    window = WordMazeApp()

    
    GlobalBlur(window.winId(), Dark=True, Acrylic=True)

    window.showFullScreen()
    sys.exit(app.exec_())
