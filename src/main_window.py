import sys
import random
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QStackedWidget, QFrame, QComboBox, QLineEdit,
    QGraphicsDropShadowEffect, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QFont, QPixmap, QPainter

try:
    from BlurWindow.blurWindow import GlobalBlur
except Exception:
    GlobalBlur = None

try:
    from .game_state import GameState
    from . import word_loader
    from . import progress_manager
except Exception:
    here = Path(__file__).resolve()
    sys.path.insert(0, str(here.parent.parent))
    from src.game_state import GameState
    from src import word_loader
    from src import progress_manager


BASE_WIDTH = 1280.0
BASE_HEIGHT = 720.0
UI_SCALE = 1.0
SAFE_AREA = 0.90

PLAYER_SPECIAL = {"ayla": "mujtaba loves you Ayla"}

BACKGROUND_LIGHT = Path("assets/Background/BACK.jpg")
BACKGROUND_DARK = Path("assets/Background/BACKdark.jpg")


def S(x: float) -> int:
    return max(1, int(x * UI_SCALE))


def F(x: float) -> int:
    return max(1, int(x * UI_SCALE))


def compute_ui_scale(w: int, h: int, max_word_len: int) -> float:
    base_margin = 40
    base_main_spacing = 26
    base_left_card_w = 420

    base_key_size = 70
    base_key_spacing = 12
    key_cols = 10
    base_keyboard_w = key_cols * base_key_size + (key_cols - 1) * base_key_spacing

    base_slot_size = 90
    base_slot_spacing = 12
    base_slots_w = max_word_len * base_slot_size + (max_word_len - 1) * base_slot_spacing

    base_right_min_w = max(base_keyboard_w, base_slots_w)
    base_required_w = (2 * base_margin) + base_main_spacing + base_left_card_w + base_right_min_w

    avail_w = w * SAFE_AREA
    avail_h = h * SAFE_AREA
    s = min(avail_w / base_required_w, avail_h / BASE_HEIGHT)
    return max(0.75, min(1.60, float(s)))


STYLESHEET = """
QMainWindow { background: transparent; }
QLabel { color: #F9FAFB; font-family: 'Segoe UI', sans-serif; }

QFrame#GlassCard {
    background-color: rgba(15, 23, 42, 0.60);
    border: 1px solid rgba(255, 255, 255, 0.28);
    border-radius: 30px;
}

QFrame#MenuCard {
    background-color: rgba(15, 23, 42, 0.60);
    border: 1px solid rgba(255, 255, 255, 0.30);
    border-radius: 34px;
}

QPushButton {
    border-radius: 20px;
    padding: 10px 18px;
    font-weight: 600;
    font-size: 14px;
    font-family: 'Segoe UI', sans-serif;
}

QPushButton#PrimaryButton { background-color: #1A73E8; color: white; border: none; }
QPushButton#PrimaryButton:hover { background-color: #1557B0; }

QPushButton#SecondaryButton { background-color: #FACC15; color: #111827; border: none; border-radius: 24px; padding: 10px 22px; }
QPushButton#SecondaryButton:hover { background-color: #EAB308; }

QPushButton#GhostButton {
    background-color: rgba(0,0,0,0);
    color: #F9FAFB;
    border: 1px solid rgba(249, 250, 251, 0.45);
}
QPushButton#GhostButton:hover { background-color: rgba(15, 23, 42, 0.45); }

QPushButton#KeyButton {
    background-color: rgba(15, 23, 42, 0.72);
    border: 1px solid rgba(255, 255, 255, 0.18);
    color: rgba(248, 250, 252, 0.95);
    border-radius: 18px;
}
QPushButton#KeyButton:hover { background-color: rgba(248, 250, 252, 0.12); }
QPushButton#KeyButton:disabled { border: 1px solid rgba(148, 163, 184, 0.2); color: rgba(248,250,252,0.25); }

QPushButton#ExitButton {
    background-color: rgba(15, 23, 42, 0.85);
    color: #F9FAFB;
    border-radius: 20px;
    border: 1px solid rgba(248, 250, 252, 0.45);
    font-size: 16px;
    font-weight: 800;
}
QPushButton#ExitButton:hover { background-color: rgba(239, 68, 68, 0.90); }

QPushButton#PillButton {
    background-color: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(148, 163, 184, 0.45);
    color: rgba(248, 250, 252, 0.92);
    border-radius: 18px;
    padding: 8px 14px;
}
QPushButton#PillButton:hover { background-color: rgba(248, 250, 252, 0.12); }
QPushButton#PillButton:checked {
    background-color: rgba(26, 115, 232, 0.95);
    border: 1px solid rgba(26, 115, 232, 1.0);
    color: #FFFFFF;
}

QComboBox {
    background-color: rgba(15, 23, 42, 0.70);
    border: 1px solid rgba(148, 163, 184, 0.55);
    border-radius: 12px;
    color: rgba(248,250,252,0.95);
    padding: 6px 10px;
    font-size: 13px;
}
QComboBox QAbstractItemView {
    background-color: #020617;
    color: #F9FAFB;
    selection-background-color: #1A73E8;
}

QLineEdit {
    background-color: rgba(15, 23, 42, 0.70);
    border: 1px solid rgba(148, 163, 184, 0.55);
    border-radius: 12px;
    color: rgba(248,250,252,0.95);
    padding: 8px 10px;
    font-size: 13px;
}

QLabel#LetterSlot {
    background-color: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(248, 250, 252, 0.42);
    border-radius: 26px;
    color: rgba(248,250,252,0.92);
    font-size: 24px;
    font-weight: 650;
}

QLabel#PreviewLabel {
    color: rgba(248,250,252,0.88);
    font-family: 'Consolas', monospace;
}

QLabel#StatusMessage {
    color: rgba(248, 250, 252, 0.75);
    font-size: 13px;
}
"""


class GlassCard(QFrame):
    def __init__(self, parent=None, object_name: str = "GlassCard"):
        super().__init__(parent)
        self.setObjectName(object_name)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(S(42))
        shadow.setColor(QColor(0, 0, 0, 190))
        shadow.setOffset(0, S(18))
        self.setGraphicsEffect(shadow)


class AylaDialog(QMessageBox):
    def __init__(self, parent=None, message: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Message")
        self.setText(message)
        self.setIcon(QMessageBox.Information)
        self.addButton("Start", QMessageBox.AcceptRole)
        self.setStyleSheet(
            f"QLabel{{font-size:{F(18)}px;}} QPushButton{{font-size:{F(14)}px; padding:8px 14px; border-radius:12px;}}"
        )
        self.setMinimumWidth(S(560))


class MenuScreen(QWidget):
    start_game_signal = pyqtSignal(str, str, str, bool)

    def __init__(self, categories: List[str], parent=None):
        super().__init__(parent)

        self._categories = categories[:]
        self._dark = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(S(60), S(50), S(60), S(50))
        outer.setSpacing(S(20))

        outer.addStretch()

        row = QHBoxLayout()
        row.addStretch()

        card = GlassCard(object_name="MenuCard")
        card.setFixedWidth(S(920))

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(S(56), S(48), S(56), S(44))
        card_layout.setSpacing(S(18))

        topbar = QHBoxLayout()
        topbar.addStretch()

        self.btn_mode = QPushButton("Dark Mode")
        self.btn_mode.setObjectName("PillButton")
        self.btn_mode.setCheckable(True)
        self.btn_mode.setFixedHeight(S(46))
        self.btn_mode.setFixedWidth(S(180))
        self.btn_mode.setCursor(Qt.PointingHandCursor)
        self.btn_mode.clicked.connect(self._toggle_mode)
        topbar.addWidget(self.btn_mode)

        title = QLabel("Word-Maze")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", F(54), QFont.Bold))

        subtitle = QLabel("Guess the word. Beat the maze.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"color: rgba(248,250,252,0.72); font-size: {F(15)}px;")

        divider = QFrame()
        divider.setFixedHeight(S(1))
        divider.setStyleSheet("background-color: rgba(248, 250, 252, 0.16); border: none;")

        form = QWidget()
        form_layout = QGridLayout(form)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setHorizontalSpacing(S(18))
        form_layout.setVerticalSpacing(S(10))

        lbl_name = QLabel("Player Name")
        lbl_name.setStyleSheet(f"color: rgba(248,250,252,0.82); font-size: {F(13)}px; font-weight: 650;")
        self.edt_name = QLineEdit()
        self.edt_name.setPlaceholderText("Type your name...")
        self.edt_name.setFixedHeight(S(46))
        self.edt_name.textChanged.connect(self._validate)

        lbl_cat = QLabel("Category")
        lbl_cat.setStyleSheet(f"color: rgba(248,250,252,0.82); font-size: {F(13)}px; font-weight: 650;")
        self.cmb_cat = QComboBox()
        self.cmb_cat.addItems([self._pretty_cat(c) for c in self._categories])
        self.cmb_cat.setFixedHeight(S(46))
        self.cmb_cat.setStyleSheet(f"font-size: {F(14)}px;")

        lbl_diff = QLabel("Difficulty")
        lbl_diff.setStyleSheet(f"color: rgba(248,250,252,0.82); font-size: {F(13)}px; font-weight: 650;")

        diff_container = QWidget()
        diff_layout = QHBoxLayout(diff_container)
        diff_layout.setContentsMargins(0, 0, 0, 0)
        diff_layout.setSpacing(S(10))

        self.diff_buttons: Dict[str, QPushButton] = {}
        for text, key in [("Easy", "easy"), ("Medium", "medium"), ("Hard", "hard")]:
            b = QPushButton(text)
            b.setObjectName("PillButton")
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.setFixedHeight(S(46))
            b.setStyleSheet(f"font-size: {F(14)}px;")
            b.clicked.connect(lambda _=False, k=key: self._select_diff(k))
            self.diff_buttons[key] = b
            diff_layout.addWidget(b)

        self._selected_diff = "medium"
        self.diff_buttons["medium"].setChecked(True)

        form_layout.addWidget(lbl_name, 0, 0, 1, 2)
        form_layout.addWidget(self.edt_name, 1, 0, 1, 2)
        form_layout.addWidget(lbl_cat, 2, 0)
        form_layout.addWidget(lbl_diff, 2, 1)
        form_layout.addWidget(self.cmb_cat, 3, 0)
        form_layout.addWidget(diff_container, 3, 1)
        form_layout.setColumnStretch(0, 1)
        form_layout.setColumnStretch(1, 1)

        actions = QHBoxLayout()
        actions.setSpacing(S(12))

        self.btn_play = QPushButton("Play")
        self.btn_play.setObjectName("PrimaryButton")
        self.btn_play.setFixedHeight(S(58))
        self.btn_play.setCursor(Qt.PointingHandCursor)
        self.btn_play.setStyleSheet(f"font-size: {F(16)}px; font-weight: 800;")
        self.btn_play.clicked.connect(self._play)

        self.btn_quit = QPushButton("Quit")
        self.btn_quit.setObjectName("GhostButton")
        self.btn_quit.setFixedHeight(S(58))
        self.btn_quit.setCursor(Qt.PointingHandCursor)
        self.btn_quit.setStyleSheet(f"font-size: {F(16)}px; font-weight: 800;")
        self.btn_quit.clicked.connect(QApplication.instance().quit)

        actions.addWidget(self.btn_play, 1)
        actions.addWidget(self.btn_quit, 1)

        footer = QLabel("Created by: Seyedmujtaba Tabatabaee & Ayla Rasouli")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"color: rgba(248,250,252,0.55); font-size: {F(12)}px;")

        card_layout.addLayout(topbar)
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(S(6))
        card_layout.addWidget(divider)
        card_layout.addSpacing(S(10))
        card_layout.addWidget(form)
        card_layout.addSpacing(S(10))
        card_layout.addLayout(actions)
        card_layout.addSpacing(S(10))
        card_layout.addWidget(footer)

        row.addWidget(card)
        row.addStretch()

        outer.addLayout(row)
        outer.addStretch()

        self._validate()

    def _pretty_cat(self, c: str) -> str:
        return c.replace("_", " ").title()

    def _raw_cat(self, pretty: str) -> str:
        for c in self._categories:
            if self._pretty_cat(c) == pretty:
                return c
        return pretty.lower().replace(" ", "_")

    def _select_diff(self, key: str):
        self._selected_diff = key
        for k, b in self.diff_buttons.items():
            b.setChecked(k == key)

    def _validate(self):
        ok = bool(self.edt_name.text().strip())
        self.btn_play.setEnabled(ok)

    def _toggle_mode(self):
        self._dark = self.btn_mode.isChecked()
        self.btn_mode.setText("Light Mode" if self._dark else "Dark Mode")

    def current_mode_dark(self) -> bool:
        return self._dark

    def _play(self):
        name = self.edt_name.text().strip()
        if not name:
            return
        category = self._raw_cat(self.cmb_cat.currentText())
        difficulty = self._selected_diff
        self.start_game_signal.emit(name, category, difficulty, self._dark)


class GameScreen(QWidget):
    go_result_signal = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.player_name: str = ""
        self.category: str = ""
        self.difficulty: str = ""
        self.state: Optional[GameState] = None
        self.word: str = ""

        self._word_set: Set[str] = set()
        self._wrong: List[str] = []
        self._keys: Dict[str, QPushButton] = {}
        self._slots: List[QLabel] = []
        self._life_dots: List[QLabel] = []

        self._style_key_correct = (
            "background-color: rgba(191, 219, 254, 0.95);"
            "color: #020617; border-radius: 20px; font-weight: 900;"
        )
        self._style_key_wrong = (
            "background-color: rgba(239, 68, 68, 0.90);"
            "color: white; border-radius: 20px; font-weight: 900;"
        )
        self._style_slot_revealed = (
            "background-color: rgba(248, 250, 252, 0.92);"
            "color: #020617;"
            "border-radius: 30px;"
            f"font-weight: 900; font-size: {F(30)}px;"
        )

        self._build()

    def _build(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(S(40), S(40), S(40), S(40))
        main_layout.setSpacing(S(26))

        left = GlassCard()
        left.setFixedWidth(S(420))
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(S(30), S(30), S(30), S(30))
        left_layout.setSpacing(S(12))

        self.lbl_info = QLabel("Game Info")
        self.lbl_info.setFont(QFont("Segoe UI", F(26), QFont.Bold))

        self.lbl_player = QLabel("Player: –")
        self.lbl_cat = QLabel("Category: –")
        self.lbl_diff = QLabel("Difficulty: –")

        self.lbl_preview = QLabel("_ _ _ _ _")
        self.lbl_preview.setObjectName("PreviewLabel")
        self.lbl_preview.setFont(QFont("Consolas", F(28), QFont.Bold))
        self.lbl_preview.setStyleSheet(f"margin-top: {S(18)}px;")

        self.lbl_wrong = QLabel("Wrong: ")
        self.lbl_wrong.setWordWrap(True)
        self.lbl_wrong.setStyleSheet(f"color: rgba(248,250,252,0.75); font-size: {F(13)}px;")

        self.lbl_lives = QLabel("Lives: 8")
        self.lbl_lives.setStyleSheet(f"color: rgba(248,250,252,0.82); font-size: {F(13)}px;")

        self.lbl_score = QLabel("Score: 0")
        self.lbl_score.setStyleSheet(f"font-size: {F(20)}px; font-weight: 900; margin-top: {S(6)}px;")

        self.btn_menu = QPushButton("Menu")
        self.btn_menu.setObjectName("GhostButton")
        self.btn_menu.setFixedHeight(S(52))
        self.btn_menu.setCursor(Qt.PointingHandCursor)

        left_layout.addWidget(self.lbl_info)
        left_layout.addSpacing(S(8))
        left_layout.addWidget(self.lbl_player)
        left_layout.addWidget(self.lbl_cat)
        left_layout.addWidget(self.lbl_diff)
        left_layout.addSpacing(S(10))
        left_layout.addWidget(self.lbl_preview)
        left_layout.addWidget(self.lbl_wrong)
        left_layout.addWidget(self.lbl_lives)
        left_layout.addStretch()
        left_layout.addWidget(self.lbl_score)
        left_layout.addSpacing(S(10))
        left_layout.addWidget(self.btn_menu)

        right_col = QVBoxLayout()
        right_col.setSpacing(S(20))

        status = GlassCard()
        status_layout = QVBoxLayout(status)
        status_layout.setContentsMargins(S(26), S(20), S(26), S(20))
        self.lbl_title = QLabel("Guess The Word")
        self.lbl_title.setFont(QFont("Segoe UI", F(38), QFont.Bold))
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_msg = QLabel("Pick a letter to begin")
        self.lbl_msg.setObjectName("StatusMessage")
        self.lbl_msg.setAlignment(Qt.AlignCenter)
        self.lbl_msg.setStyleSheet(f"font-size: {F(14)}px;")
        status_layout.addWidget(self.lbl_title)
        status_layout.addWidget(self.lbl_msg)

        self.slots_container = QWidget()
        self.slots_layout = QHBoxLayout(self.slots_container)
        self.slots_layout.setAlignment(Qt.AlignCenter)
        self.slots_layout.setSpacing(S(12))

        self.lives_container = QWidget()
        self.lives_layout = QHBoxLayout(self.lives_container)
        self.lives_layout.setAlignment(Qt.AlignCenter)
        self.lives_layout.setSpacing(S(10))
        self._build_lives_once(8)

        keyboard_card = GlassCard()
        keyboard = QGridLayout(keyboard_card)
        keyboard.setContentsMargins(S(20), S(18), S(20), S(18))
        keyboard.setSpacing(S(12))

        rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        start_cols = [0, 1, 2]
        key_font = QFont("Segoe UI", F(30), QFont.Bold)

        for r, letters in enumerate(rows):
            c0 = start_cols[r]
            for i, ch in enumerate(letters):
                b = QPushButton(ch)
                b.setObjectName("KeyButton")
                b.setFixedSize(S(70), S(70))
                b.setFont(key_font)
                b.setStyleSheet(f"font-size: {F(30)}px; font-weight: 900;")
                b.setCursor(Qt.PointingHandCursor)
                b.clicked.connect(lambda _=False, l=ch: self.guess(l))
                keyboard.addWidget(b, r, c0 + i)
                self._keys[ch] = b

        bottom = QHBoxLayout()
        bottom.setSpacing(S(14))

        self.btn_hint = QPushButton("Hint (-20)")
        self.btn_hint.setObjectName("SecondaryButton")
        self.btn_hint.setFixedHeight(S(56))
        self.btn_hint.setFixedWidth(S(180))
        self.btn_hint.setCursor(Qt.PointingHandCursor)
        self.btn_hint.clicked.connect(self.use_hint)

        self.btn_reset = QPushButton("Reset Round")
        self.btn_reset.setObjectName("GhostButton")
        self.btn_reset.setFixedHeight(S(56))
        self.btn_reset.setFixedWidth(S(200))
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_round)

        bottom.addWidget(self.btn_hint)
        bottom.addStretch()
        bottom.addWidget(self.btn_reset)

        right_col.addWidget(status)
        right_col.addWidget(self.slots_container)
        right_col.addWidget(self.lives_container)
        right_col.addWidget(keyboard_card)
        right_col.addLayout(bottom)

        main_layout.addWidget(left)
        main_layout.addLayout(right_col)

    def _build_lives_once(self, n: int):
        self._life_dots.clear()
        while self.lives_layout.count():
            it = self.lives_layout.takeAt(0)
            w = it.widget()
            if w:
                w.setParent(None)

        size = S(20)
        for _ in range(n):
            dot = QLabel()
            dot.setFixedSize(size, size)
            self._life_dots.append(dot)
            self.lives_layout.addWidget(dot)

    def _ensure_slots(self, n: int):
        if len(self._slots) == n and self._slots:
            return
        self._slots.clear()
        while self.slots_layout.count():
            it = self.slots_layout.takeAt(0)
            w = it.widget()
            if w:
                w.setParent(None)

        for _ in range(n):
            lbl = QLabel("_")
            lbl.setObjectName("LetterSlot")
            lbl.setFixedSize(S(90), S(90))
            lbl.setAlignment(Qt.AlignCenter)
            self._slots.append(lbl)
            self.slots_layout.addWidget(lbl)

    def start_round(self, player: str, category: str, difficulty: str, word: str):
        self.player_name = player
        self.category = category
        self.difficulty = difficulty
        self.word = word

        self.state = GameState(word)
        self._word_set = set(self.state.word)
        self._wrong = []

        self.lbl_player.setText(f"Player: {player}")
        self.lbl_cat.setText(f"Category: {category.replace('_',' ').title()}")
        self.lbl_diff.setText(f"Difficulty: {difficulty.title()}")

        self._ensure_slots(len(self.state.word))
        self._build_lives_once(self.state.lives)

        for b in self._keys.values():
            b.setEnabled(True)
            b.setStyleSheet(f"font-size: {F(30)}px; font-weight: 900;")

        self.lbl_msg.setText("Pick a letter to begin")
        self._render_all()

    def reset_round(self):
        if not self.state:
            return
        self.start_round(self.player_name, self.category, self.difficulty, self.word)

    def _render_all(self):
        if not self.state:
            return
        self.lbl_preview.setText(self.state.masked())
        self.lbl_wrong.setText("Wrong: " + ", ".join(self._wrong))
        self.lbl_lives.setText(f"Lives: {self.state.life}")
        self.lbl_score.setText(f"Score: {self.state.score}")

        self._ensure_slots(len(self.state.word))
        for i, ch in enumerate(self.state.word):
            lbl = self._slots[i]
            if i in self.state.revealed:
                lbl.setText(ch)
                lbl.setStyleSheet(self._style_slot_revealed)
            else:
                lbl.setText("_")
                lbl.setStyleSheet("")

        size = S(20)
        for i, dot in enumerate(self._life_dots):
            full = i < self.state.life
            color = "rgba(255,255,255,0.95)" if full else "rgba(255,255,255,0.22)"
            dot.setStyleSheet(f"background-color: {color}; border-radius: {size//2}px;")

    def guess(self, letter: str):
        if not self.state:
            return

        letter = letter.upper()
        btn = self._keys.get(letter)
        if btn:
            btn.setDisabled(True)

        res = self.state.guess(letter)
        if "error" in res:
            self.lbl_msg.setText("Invalid input.")
            if btn:
                btn.setEnabled(True)
            return

        if res.get("correct"):
            self.lbl_msg.setText(f"Nice! {letter} is in the word.")
            if btn:
                btn.setStyleSheet(self._style_key_correct + f" font-size: {F(30)}px;")
        else:
            self.lbl_msg.setText(f"Oops! {letter} is not in the word.")
            if letter not in self._wrong:
                self._wrong.append(letter)
            if btn:
                btn.setStyleSheet(self._style_key_wrong + f" font-size: {F(30)}px;")

        self._render_all()

        if self.state.is_won() or self.state.is_lost():
            result = self.state.finish_round()
            payload = {
                "player": self.player_name,
                "category": self.category,
                "difficulty": self.difficulty,
                "word": self.state.word,
                "masked": self.state.masked(),
                "score": self.state.score,
                "lives": self.state.life,
                "result": result
            }
            self.go_result_signal.emit(payload)

    def use_hint(self):
        if not self.state:
            return
        res = self.state.use_hint()
        if not res.get("used"):
            if res.get("reason") == "not_enough_score":
                self.lbl_msg.setText("Not enough points for a hint!")
            else:
                self.lbl_msg.setText("Hint not available.")
        else:
            self.lbl_msg.setText("Hint used.")
        self._render_all()
        if self.state.is_won():
            result = self.state.finish_round()
            payload = {
                "player": self.player_name,
                "category": self.category,
                "difficulty": self.difficulty,
                "word": self.state.word,
                "masked": self.state.masked(),
                "score": self.state.score,
                "lives": self.state.life,
                "result": result
            }
            self.go_result_signal.emit(payload)


class ResultScreen(QWidget):
    next_round_signal = pyqtSignal()
    menu_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(S(60), S(50), S(60), S(50))
        layout.addStretch()

        row = QHBoxLayout()
        row.addStretch()

        self.card = GlassCard()
        self.card.setFixedWidth(S(780))
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(S(54), S(44), S(54), S(44))
        card_layout.setSpacing(S(16))

        self.lbl_title = QLabel("Round Result")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setFont(QFont("Segoe UI", F(42), QFont.Bold))

        self.lbl_sub = QLabel("")
        self.lbl_sub.setAlignment(Qt.AlignCenter)
        self.lbl_sub.setStyleSheet(f"color: rgba(248,250,252,0.78); font-size: {F(16)}px;")

        self.lbl_word = QLabel("")
        self.lbl_word.setAlignment(Qt.AlignCenter)
        self.lbl_word.setStyleSheet(f"color: rgba(248,250,252,0.92); font-size: {F(18)}px; font-weight: 800;")

        self.lbl_stats = QLabel("")
        self.lbl_stats.setAlignment(Qt.AlignCenter)
        self.lbl_stats.setStyleSheet(f"color: rgba(248,250,252,0.72); font-size: {F(14)}px;")

        actions = QHBoxLayout()
        actions.setSpacing(S(12))

        self.btn_next = QPushButton("Next Round")
        self.btn_next.setObjectName("PrimaryButton")
        self.btn_next.setFixedHeight(S(60))
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.setStyleSheet(f"font-size: {F(16)}px; font-weight: 900;")
        self.btn_next.clicked.connect(self.next_round_signal.emit)

        self.btn_menu = QPushButton("Menu")
        self.btn_menu.setObjectName("GhostButton")
        self.btn_menu.setFixedHeight(S(60))
        self.btn_menu.setCursor(Qt.PointingHandCursor)
        self.btn_menu.setStyleSheet(f"font-size: {F(16)}px; font-weight: 900;")
        self.btn_menu.clicked.connect(self.menu_signal.emit)

        actions.addWidget(self.btn_next, 1)
        actions.addWidget(self.btn_menu, 1)

        card_layout.addWidget(self.lbl_title)
        card_layout.addWidget(self.lbl_sub)
        card_layout.addSpacing(S(4))
        card_layout.addWidget(self.lbl_word)
        card_layout.addWidget(self.lbl_stats)
        card_layout.addSpacing(S(10))
        card_layout.addLayout(actions)

        row.addWidget(self.card)
        row.addStretch()

        layout.addLayout(row)
        layout.addStretch()

    def set_result(self, won: bool, word: str, round_score: int, bonus: int, mistakes: int):
        self.lbl_title.setText("You Win!" if won else "Game Over")
        self.lbl_title.setStyleSheet(
            f"color: {'#4ADE80' if won else '#EF4444'}; font-size: {F(48)}px; font-weight: 900;"
        )
        self.lbl_sub.setText("Nice run. Next round is ready." if won else "No lives left. Try a new round!")
        self.lbl_word.setText(f"The word was: {word}")
        extra = f" (Bonus +{bonus})" if bonus else ""
        self.lbl_stats.setText(f"Round Score: {round_score}{extra}   |   Mistakes: {mistakes}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.root = Path(__file__).resolve().parents[1]
        self.words_path = self.root / "data" / "words.json"
        self.save_path = self.root / "data" / "save_data.json"

        if self.words_path.exists():
            word_loader.load(str(self.words_path))
            categories = word_loader.categories()
        else:
            categories = []

        self._max_word_len = 12
        try:
            if self.words_path.exists():
                import json as _json
                obj = _json.loads(self.words_path.read_text(encoding="utf-8"))
                mx = 1
                for cat in obj:
                    for diff in obj[cat]:
                        for w in obj[cat][diff]:
                            mx = max(mx, len(str(w)))
                self._max_word_len = max(6, mx)
        except Exception:
            pass

        self.setWindowTitle("Word-Maze")
        self.setMinimumSize(900, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.menu = MenuScreen(categories)
        self.game = GameScreen()
        self.result = ResultScreen()

        self.stack.addWidget(self.menu)
        self.stack.addWidget(self.game)
        self.stack.addWidget(self.result)

        self.menu.start_game_signal.connect(self._start_from_menu)
        self.game.go_result_signal.connect(self._show_result)
        self.result.next_round_signal.connect(self._next_round)
        self.result.menu_signal.connect(self._go_menu)

        self.game.btn_menu.clicked.connect(self._go_menu)

        self.exit_btn = QPushButton("✕", self)
        self.exit_btn.setObjectName("ExitButton")
        self.exit_btn.setCursor(Qt.PointingHandCursor)
        self.exit_btn.clicked.connect(QApplication.instance().quit)

        self._dark_bg = False
        self._bg_cache: Dict[Tuple[bool, int, int], QPixmap] = {}

        self._rebuild_pending = False
        self._last_scale: Optional[float] = None

    def current_bg_path(self) -> Path:
        rel = BACKGROUND_DARK if self._dark_bg else BACKGROUND_LIGHT
        return (self.root / rel)

    def _bg_pixmap_for(self, w: int, h: int) -> Optional[QPixmap]:
        key = (self._dark_bg, w, h)
        if key in self._bg_cache:
            return self._bg_cache[key]

        p = self.current_bg_path()
        if not p.exists():
            return None

        src = QPixmap(str(p))
        if src.isNull():
            return None

        scaled = src.scaled(w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        if scaled.width() == w and scaled.height() == h:
            out = scaled
        else:
            x = max(0, (scaled.width() - w) // 2)
            y = max(0, (scaled.height() - h) // 2)
            out = scaled.copy(x, y, w, h)

        self._bg_cache[key] = out
        if len(self._bg_cache) > 6:
            self._bg_cache = dict(list(self._bg_cache.items())[-4:])
        return out

    def paintEvent(self, event):
        painter = QPainter(self)
        pm = self._bg_pixmap_for(self.width(), self.height())
        if pm is not None:
            painter.drawPixmap(0, 0, pm)
        else:
            painter.fillRect(self.rect(), QColor(10, 14, 24))
        super().paintEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        m = S(18)
        self.exit_btn.setFixedSize(S(44), S(44))
        self.exit_btn.move(self.width() - self.exit_btn.width() - m, m)

        global UI_SCALE
        new_scale = compute_ui_scale(self.width(), self.height(), self._max_word_len)
        if self._last_scale is None:
            self._last_scale = new_scale
            UI_SCALE = new_scale
            self._schedule_rebuild()
            return

        if abs(new_scale - self._last_scale) >= 0.03:
            self._last_scale = new_scale
            UI_SCALE = new_scale
            self._schedule_rebuild()

        self._bg_cache.pop((self._dark_bg, self.width(), self.height()), None)
        self.update()

    def _schedule_rebuild(self):
        if self._rebuild_pending:
            return
        self._rebuild_pending = True
        idx = self.stack.currentIndex()
        QTimer.singleShot(0, lambda: self._do_rebuild(idx))

    def _do_rebuild(self, return_index: int):
        self._rebuild_pending = False

        old_menu = self.menu
        old_game = self.game
        old_result = self.result

        try:
            cats = word_loader.categories()
        except Exception:
            cats = []

        self.menu = MenuScreen(cats)
        self.game = GameScreen()
        self.result = ResultScreen()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.stack.addWidget(self.menu)
        self.stack.addWidget(self.game)
        self.stack.addWidget(self.result)

        self.menu.start_game_signal.connect(self._start_from_menu)
        self.game.go_result_signal.connect(self._show_result)
        self.result.next_round_signal.connect(self._next_round)
        self.result.menu_signal.connect(self._go_menu)
        self.game.btn_menu.clicked.connect(self._go_menu)

        self.stack.setCurrentIndex(max(0, min(return_index, 2)))

        if old_menu:
            old_menu.setParent(None)
            old_menu.deleteLater()
        if old_game:
            old_game.setParent(None)
            old_game.deleteLater()
        if old_result:
            old_result.setParent(None)
            old_result.deleteLater()

        self.update()

    def _ensure_blur(self):
        if GlobalBlur is None:
            return
        try:
            GlobalBlur(self.winId(), Dark=True, Acrylic=True)
        except TypeError:
            try:
                GlobalBlur(self.winId(), Dark=True)
            except Exception:
                pass
        except Exception:
            pass

    def _start_from_menu(self, player: str, category: str, difficulty: str, dark_mode: bool):
        self._dark_bg = bool(dark_mode)
        self._bg_cache.clear()
        self.update()

        name_key = player.strip().lower()
        if name_key in PLAYER_SPECIAL:
            dlg = AylaDialog(self, PLAYER_SPECIAL[name_key])
            dlg.exec_()

        try:
            word = word_loader.random_word(category, difficulty)
        except Exception:
            QMessageBox.warning(self, "No words", "No words found for this category/difficulty.")
            return

        self._save_player_name(player)

        self.game.start_round(player, category, difficulty, word)
        self.stack.setCurrentIndex(1)

    def _save_player_name(self, player: str):
        try:
            data = progress_manager.progress(str(self.save_path))
        except Exception:
            data = {"total_score": 0, "games_played": 0, "wins": 0, "losses": 0}
        data["player_name"] = player
        try:
            progress_manager.save_progress(str(self.save_path), data)
        except Exception:
            try:
                self.save_path.parent.mkdir(parents=True, exist_ok=True)
                import json as _json
                self.save_path.write_text(_json.dumps(data, indent=2), encoding="utf-8")
            except Exception:
                pass

    def _show_result(self, payload: dict):
        res = payload.get("result", {})
        won = bool(res.get("won"))
        word = payload.get("word", "")
        round_score = int(res.get("round_score", payload.get("score", 0)))
        bonus = int(res.get("bonus", 0))
        mistakes = int(res.get("mistakes", 0))

        try:
            progress_manager.update_progress(str(self.save_path), res)
        except Exception:
            pass

        self.result.set_result(won, word, round_score, bonus, mistakes)
        self.stack.setCurrentIndex(2)

    def _next_round(self):
        player = self.game.player_name
        category = self.game.category
        difficulty = self.game.difficulty
        if not player or not category or not difficulty:
            self._go_menu()
            return
        try:
            word = word_loader.random_word(category, difficulty)
        except Exception:
            self._go_menu()
            return
        self.game.start_round(player, category, difficulty, word)
        self.stack.setCurrentIndex(1)

    def _go_menu(self):
        self.stack.setCurrentIndex(0)

    def set_dark_background(self, dark: bool):
        self._dark_bg = bool(dark)
        self._bg_cache.clear()
        self.update()

    def showFullScreen(self):
        super().showFullScreen()
        QTimer.singleShot(0, self._ensure_blur)


def run():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)

    w = MainWindow()
    w.showFullScreen()

    def first_scale():
        global UI_SCALE
        UI_SCALE = compute_ui_scale(w.width(), w.height(), w._max_word_len)
        w._last_scale = UI_SCALE
        w._schedule_rebuild()

    QTimer.singleShot(0, first_scale)
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()

