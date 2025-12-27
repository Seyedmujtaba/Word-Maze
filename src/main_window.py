# src/main_window.py
import os
import sys

from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QPixmap, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QStackedWidget, QFrame, QComboBox, QLineEdit,
    QGraphicsDropShadowEffect, QSizePolicy, QDialog
)

from .game_state import GameState
from . import word_loader
from .progress_manager import progress as load_progress, update_progress

try:
    from BlurWindow.blurWindow import GlobalBlur
except Exception:
    GlobalBlur = None


BASE_WIDTH = 1280.0
BASE_HEIGHT = 720.0
UI_SCALE = 1.0


def S(x: float) -> int:
    return max(1, int(x * UI_SCALE))


def F(x: float) -> int:
    return max(1, int(x * UI_SCALE))


def clear_layout(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w is not None:
            w.setParent(None)
            continue
        sub = item.layout()
        if sub is not None:
            clear_layout(sub)


def assets_path(*parts: str) -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(here, ".."))
    return os.path.join(root, *parts)


def data_path(*parts: str) -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(here, ".."))
    return os.path.join(root, "data", *parts)


def fit_cover(pix: QPixmap, target: QSize) -> QPixmap:
    if pix.isNull() or target.width() <= 0 or target.height() <= 0:
        return pix
    tw, th = target.width(), target.height()
    sw, sh = pix.width(), pix.height()
    if sw <= 0 or sh <= 0:
        return pix
    scale = max(tw / sw, th / sh)
    nw = int(sw * scale)
    nh = int(sh * scale)
    scaled = pix.scaled(nw, nh, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    x = max(0, (nw - tw) // 2)
    y = max(0, (nh - th) // 2)
    return scaled.copy(x, y, tw, th)


STYLESHEET = """
QMainWindow {
    background: transparent;
}

QLabel {
    color: rgba(248, 250, 252, 0.92);
    font-family: 'Segoe UI', sans-serif;
}

QFrame#GlassCard {
    background-color: rgba(15, 23, 42, 0.60);
    border: 1px solid rgba(255, 255, 255, 0.28);
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

QLineEdit, QComboBox {
    background-color: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(148, 163, 184, 0.45);
    border-radius: 12px;
    color: rgba(248, 250, 252, 0.92);
    padding: 10px 12px;
}

QComboBox QAbstractItemView {
    background-color: #020617;
    color: rgba(248, 250, 252, 0.92);
    selection-background-color: rgba(26, 115, 232, 0.95);
}

QPushButton {
    border-radius: 18px;
    padding: 10px 18px;
    font-weight: 600;
    font-family: 'Segoe UI', sans-serif;
}

QPushButton#PrimaryButton {
    background-color: rgba(26, 115, 232, 0.95);
    color: white;
    border: none;
}
QPushButton#PrimaryButton:hover { background-color: rgba(26, 115, 232, 1.0); }
QPushButton#PrimaryButton:disabled { background-color: rgba(26, 115, 232, 0.35); color: rgba(255,255,255,0.55); }

QPushButton#GhostButton {
    background-color: rgba(15, 23, 42, 0.55);
    color: rgba(248, 250, 252, 0.92);
    border: 1px solid rgba(148, 163, 184, 0.35);
}
QPushButton#GhostButton:hover { background-color: rgba(248, 250, 252, 0.10); }

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

QPushButton#SecondaryButton {
    background-color: rgba(250, 204, 21, 0.98);
    color: rgba(2, 6, 23, 0.95);
    border: none;
}
QPushButton#SecondaryButton:hover { background-color: rgba(234, 179, 8, 0.98); }

QPushButton#KeyButton {
    background-color: rgba(15, 23, 42, 0.60);
    border: 1px solid rgba(148, 163, 184, 0.28);
    color: rgba(248, 250, 252, 0.92);
    border-radius: 18px;
}
QPushButton#KeyButton:hover { background-color: rgba(248, 250, 252, 0.10); }
QPushButton#KeyButton:disabled {
    background-color: rgba(2, 6, 23, 0.35);
    color: rgba(248, 250, 252, 0.25);
    border: 1px solid rgba(148, 163, 184, 0.15);
}

QLabel#LetterSlot {
    background-color: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(248, 250, 252, 0.18);
    border-radius: 22px;
    color: rgba(248, 250, 252, 0.92);
    font-weight: 700;
}

QPushButton#ExitButton {
    background-color: rgba(15, 23, 42, 0.70);
    color: rgba(248, 250, 252, 0.92);
    border-radius: 18px;
    border: 1px solid rgba(148, 163, 184, 0.35);
    font-weight: 800;
}
QPushButton#ExitButton:hover {
    background-color: rgba(239, 68, 68, 0.90);
    border: 1px solid rgba(239, 68, 68, 1.0);
}

QPushButton#ThemeButton {
    background-color: rgba(15, 23, 42, 0.55);
    color: rgba(248, 250, 252, 0.92);
    border: 1px solid rgba(148, 163, 184, 0.35);
    border-radius: 16px;
    font-weight: 700;
}
QPushButton#ThemeButton:hover { background-color: rgba(248, 250, 252, 0.10); }
"""


class GlassCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("GlassCard")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(S(48))
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, S(18))
        self.setGraphicsEffect(shadow)


class AylaDialog(QDialog):
    proceed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setModal(True)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(S(24), S(24), S(24), S(24))

        card = GlassCard()
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(S(36), S(32), S(36), S(28))
        lay.setSpacing(S(18))

        title = QLabel("Message")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", F(20), QFont.Bold))

        msg = QLabel("mujtaba loves you Ayla")
        msg.setWordWrap(True)
        msg.setAlignment(Qt.AlignCenter)
        msg.setFont(QFont("Segoe UI", F(18), QFont.DemiBold))
        msg.setStyleSheet("color: rgba(248, 250, 252, 0.92);")

        btn = QPushButton("Start")
        btn.setObjectName("PrimaryButton")
        btn.setFixedHeight(S(54))
        btn.setFont(QFont("Segoe UI", F(16), QFont.Bold))
        btn.clicked.connect(self._go)

        lay.addWidget(title)
        lay.addWidget(msg)
        lay.addSpacing(S(6))
        lay.addWidget(btn)

        outer.addWidget(card)

        self.setFixedSize(S(520), S(260))

    def _go(self):
        self.accept()
        self.proceed.emit()


class MainMenuScreen(QWidget):
    start_game_signal = pyqtSignal(str, str, str)

    def __init__(self, categories):
        super().__init__()
        self.categories = categories
        self._dark = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(S(60), S(50), S(60), S(50))
        outer.setSpacing(S(20))

        outer.addStretch()

        row = QHBoxLayout()
        row.addStretch()

        self.menu_card = GlassCard()
        self.menu_card.setMinimumWidth(S(860))
        self.menu_card.setMaximumWidth(S(1100))

        card_layout = QVBoxLayout(self.menu_card)
        card_layout.setContentsMargins(S(56), S(46), S(56), S(46))
        card_layout.setSpacing(S(18))

        top_row = QHBoxLayout()
        top_row.addStretch()

        self.btn_theme = QPushButton("Dark Mode")
        self.btn_theme.setObjectName("ThemeButton")
        self.btn_theme.setFixedHeight(S(46))
        self.btn_theme.setFixedWidth(S(180))
        self.btn_theme.setFont(QFont("Segoe UI", F(14), QFont.Bold))
        self.btn_theme.clicked.connect(self._toggle_theme)
        top_row.addWidget(self.btn_theme)

        title = QLabel("Word-Maze")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", F(52), QFont.Bold))

        subtitle = QLabel("Guess the word. Beat the maze.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setObjectName("MenuSubtitle")
        subtitle.setFont(QFont("Segoe UI", F(14)))

        divider = QFrame()
        divider.setFixedHeight(S(1))
        divider.setStyleSheet("background-color: rgba(248, 250, 252, 0.16); border: none;")

        form = QWidget()
        form_layout = QGridLayout(form)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setHorizontalSpacing(S(18))
        form_layout.setVerticalSpacing(S(10))

        label_name = QLabel("Player Name")
        label_name.setObjectName("MenuFieldLabel")
        label_name.setFont(QFont("Segoe UI", F(13), QFont.DemiBold))

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Type your name...")
        self.input_name.setFixedHeight(S(48))
        self.input_name.setFont(QFont("Segoe UI", F(14)))
        self.input_name.textChanged.connect(self._validate)

        label_cat = QLabel("Category")
        label_cat.setObjectName("MenuFieldLabel")
        label_cat.setFont(QFont("Segoe UI", F(13), QFont.DemiBold))

        self.category_combo = QComboBox()
        self.category_combo.addItems(self.categories)
        self.category_combo.setFixedHeight(S(48))
        self.category_combo.setFont(QFont("Segoe UI", F(14)))

        label_diff = QLabel("Difficulty")
        label_diff.setObjectName("MenuFieldLabel")
        label_diff.setFont(QFont("Segoe UI", F(13), QFont.DemiBold))

        diff_container = QWidget()
        diff_layout = QHBoxLayout(diff_container)
        diff_layout.setContentsMargins(0, 0, 0, 0)
        diff_layout.setSpacing(S(10))

        self.diff_buttons = []
        for text in ["Easy", "Medium", "Hard"]:
            b = QPushButton(text)
            b.setObjectName("PillButton")
            b.setCheckable(True)
            b.setFixedHeight(S(48))
            b.setFont(QFont("Segoe UI", F(14), QFont.DemiBold))
            b.clicked.connect(lambda checked, btn=b: self._select_diff(btn))
            diff_layout.addWidget(b)
            self.diff_buttons.append(b)

        if len(self.diff_buttons) >= 2:
            self.diff_buttons[1].setChecked(True)

        form_layout.addWidget(label_name, 0, 0, 1, 2)
        form_layout.addWidget(self.input_name, 1, 0, 1, 2)
        form_layout.addWidget(label_cat, 2, 0)
        form_layout.addWidget(label_diff, 2, 1)
        form_layout.addWidget(self.category_combo, 3, 0)
        form_layout.addWidget(diff_container, 3, 1)
        form_layout.setColumnStretch(0, 1)
        form_layout.setColumnStretch(1, 1)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(S(12))

        self.btn_play = QPushButton("Play")
        self.btn_play.setObjectName("PrimaryButton")
        self.btn_play.setFixedHeight(S(58))
        self.btn_play.setFont(QFont("Segoe UI", F(16), QFont.Bold))
        self.btn_play.clicked.connect(self._play)

        self.btn_quit = QPushButton("Quit")
        self.btn_quit.setObjectName("GhostButton")
        self.btn_quit.setFixedHeight(S(58))
        self.btn_quit.setFont(QFont("Segoe UI", F(16), QFont.Bold))
        self.btn_quit.clicked.connect(QApplication.instance().quit)

        actions_layout.addWidget(self.btn_play, 1)
        actions_layout.addWidget(self.btn_quit, 1)

        footer = QLabel("Created by: Seyedmujtaba Tabatabaee & Ayla Rasouli")
        footer.setAlignment(Qt.AlignCenter)
        footer.setObjectName("MenuFooter")
        footer.setFont(QFont("Segoe UI", F(11)))

        card_layout.addLayout(top_row)
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(S(6))
        card_layout.addWidget(divider)
        card_layout.addSpacing(S(6))
        card_layout.addWidget(form)
        card_layout.addSpacing(S(10))
        card_layout.addLayout(actions_layout)
        card_layout.addSpacing(S(10))
        card_layout.addWidget(footer)

        row.addWidget(self.menu_card)
        row.addStretch()

        outer.addLayout(row)
        outer.addStretch()

        self._validate()

    def _select_diff(self, btn: QPushButton):
        for b in self.diff_buttons:
            b.setChecked(b is btn)

    def _get_diff(self) -> str:
        for b in self.diff_buttons:
            if b.isChecked():
                return b.text()
        return "Medium"

    def _validate(self):
        name = self.input_name.text().strip()
        self.btn_play.setEnabled(bool(name))

    def _play(self):
        name = self.input_name.text().strip()
        if not name:
            return
        cat = self.category_combo.currentText()
        diff = self._get_diff()
        self.start_game_signal.emit(name, cat, diff)

    def _toggle_theme(self):
        self._dark = not self._dark
        self.btn_theme.setText("Light Mode" if self._dark else "Dark Mode")
        self.parent().parent().set_dark_mode(self._dark)


class GameScreen(QWidget):
    round_finished = pyqtSignal(dict)
    go_menu = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.player_name = ""
        self.category = ""
        self.difficulty = ""

        self.state = None
        self.current_word = ""
        self.word_set = set()

        self.key_buttons = {}
        self.slot_labels = []
        self.life_dots = []

        self.max_lives = 8

        self._style_key_correct = (
            "background-color: rgba(191, 219, 254, 0.95);"
            "color: rgba(2, 6, 23, 0.95);"
            "border-radius: 18px;"
            "font-weight: 800;"
        )
        self._style_key_wrong = (
            "background-color: rgba(239, 68, 68, 0.90);"
            "color: rgba(248, 250, 252, 0.95);"
            "border-radius: 18px;"
            "font-weight: 800;"
        )
        self._style_slot_revealed = (
            "background-color: rgba(248, 250, 252, 0.92);"
            "color: rgba(2, 6, 23, 0.95);"
            "border-radius: 22px;"
            "font-weight: 900;"
        )

        self._build_ui()

    def _build_ui(self):
        main = QHBoxLayout(self)
        main.setContentsMargins(S(60), S(55), S(60), S(55))
        main.setSpacing(S(26))

        self.left_card = GlassCard()
        self.left_card.setFixedWidth(S(420))
        left = QVBoxLayout(self.left_card)
        left.setContentsMargins(S(32), S(30), S(32), S(30))
        left.setSpacing(S(14))

        title = QLabel("Game Info")
        title.setFont(QFont("Segoe UI", F(26), QFont.Bold))

        self.lbl_player = QLabel("Player: -")
        self.lbl_cat = QLabel("Category: -")
        self.lbl_diff = QLabel("Difficulty: -")

        self.lbl_preview = QLabel("")
        self.lbl_preview.setFont(QFont("Consolas", F(22)))
        self.lbl_preview.setStyleSheet("color: rgba(250, 204, 21, 0.95); margin-top: 18px;")

        self.lbl_wrong = QLabel("Wrong: ")
        self.lbl_wrong.setWordWrap(True)
        self.lbl_wrong.setStyleSheet(f"font-size: {F(12)}px; color: rgba(248,250,252,0.72);")

        self.lbl_lives = QLabel("Lives: 8")
        self.lbl_lives.setStyleSheet(f"font-size: {F(12)}px; color: rgba(248,250,252,0.72);")

        self.lbl_score = QLabel("Score: 0")
        self.lbl_score.setFont(QFont("Segoe UI", F(18), QFont.Bold))
        self.lbl_score.setStyleSheet("margin-top: 10px;")

        left.addWidget(title)
        left.addSpacing(S(4))
        left.addWidget(self.lbl_player)
        left.addWidget(self.lbl_cat)
        left.addWidget(self.lbl_diff)
        left.addSpacing(S(12))
        left.addWidget(self.lbl_preview)
        left.addSpacing(S(4))
        left.addWidget(self.lbl_wrong)
        left.addWidget(self.lbl_lives)
        left.addStretch()
        left.addWidget(self.lbl_score)

        self.btn_menu = QPushButton("Menu")
        self.btn_menu.setObjectName("GhostButton")
        self.btn_menu.setFixedHeight(S(54))
        self.btn_menu.setFont(QFont("Segoe UI", F(15), QFont.Bold))
        self.btn_menu.clicked.connect(self.go_menu.emit)
        left.addSpacing(S(10))
        left.addWidget(self.btn_menu)

        right = QVBoxLayout()
        right.setSpacing(S(18))

        status_card = GlassCard()
        status = QVBoxLayout(status_card)
        status.setContentsMargins(S(30), S(22), S(30), S(22))
        status.setSpacing(S(8))

        self.lbl_title = QLabel("Guess The Word")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setFont(QFont("Segoe UI", F(34), QFont.Bold))

        self.lbl_msg = QLabel("Pick a letter to begin")
        self.lbl_msg.setAlignment(Qt.AlignCenter)
        self.lbl_msg.setStyleSheet(f"font-size: {F(14)}px; color: rgba(248,250,252,0.72);")

        status.addWidget(self.lbl_title)
        status.addWidget(self.lbl_msg)

        self.slots_container = QWidget()
        self.slots_layout = QHBoxLayout(self.slots_container)
        self.slots_layout.setContentsMargins(0, 0, 0, 0)
        self.slots_layout.setAlignment(Qt.AlignCenter)
        self.slots_layout.setSpacing(S(12))

        self.lives_container = QWidget()
        self.lives_layout = QHBoxLayout(self.lives_container)
        self.lives_layout.setContentsMargins(0, 0, 0, 0)
        self.lives_layout.setAlignment(Qt.AlignCenter)
        self.lives_layout.setSpacing(S(10))

        self._build_lives_ui()

        keyboard_card = GlassCard()
        keyboard = QGridLayout(keyboard_card)
        keyboard.setContentsMargins(S(26), S(22), S(26), S(22))
        keyboard.setHorizontalSpacing(S(12))
        keyboard.setVerticalSpacing(S(12))

        rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        start_cols = [0, 1, 2]

        key_font = QFont("Segoe UI", F(22), QFont.Bold)
        key_size = S(72)

        for r, row_letters in enumerate(rows):
            c0 = start_cols[r]
            for i, ch in enumerate(row_letters):
                b = QPushButton(ch)
                b.setObjectName("KeyButton")
                b.setFixedSize(key_size, key_size)
                b.setFont(key_font)
                b.clicked.connect(lambda checked, letter=ch: self.guess(letter))
                self.key_buttons[ch] = b
                keyboard.addWidget(b, r, c0 + i)

        bottom = QHBoxLayout()
        bottom.setSpacing(S(16))

        self.btn_hint = QPushButton("Hint (-20)")
        self.btn_hint.setObjectName("SecondaryButton")
        self.btn_hint.setFixedHeight(S(56))
        self.btn_hint.setFixedWidth(S(220))
        self.btn_hint.setFont(QFont("Segoe UI", F(15), QFont.Bold))
        self.btn_hint.clicked.connect(self.use_hint)

        self.btn_reset = QPushButton("Reset Round")
        self.btn_reset.setObjectName("GhostButton")
        self.btn_reset.setFixedHeight(S(56))
        self.btn_reset.setFixedWidth(S(220))
        self.btn_reset.setFont(QFont("Segoe UI", F(15), QFont.Bold))
        self.btn_reset.clicked.connect(self.reset_round)

        bottom.addWidget(self.btn_hint)
        bottom.addStretch()
        bottom.addWidget(self.btn_reset)

        right.addWidget(status_card)
        right.addWidget(self.slots_container)
        right.addWidget(self.lives_container)
        right.addWidget(keyboard_card)
        right.addLayout(bottom)

        main.addWidget(self.left_card)
        main.addLayout(right)

    def _build_lives_ui(self):
        clear_layout(self.lives_layout)
        self.life_dots = []
        size = S(14)
        for _ in range(self.max_lives):
            dot = QLabel()
            dot.setFixedSize(size, size)
            dot.setStyleSheet(f"background-color: rgba(248,250,252,0.18); border-radius: {size//2}px;")
            self.life_dots.append(dot)
            self.lives_layout.addWidget(dot)

    def _ensure_slots(self):
        if self.state is None:
            return
        if len(self.slot_labels) == len(self.state.word) and self.slot_labels:
            return
        clear_layout(self.slots_layout)
        self.slot_labels = []
        size = S(76)
        font = QFont("Segoe UI", F(26), QFont.Bold)
        for _ in self.state.word:
            lbl = QLabel("_")
            lbl.setObjectName("LetterSlot")
            lbl.setFixedSize(size, size)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFont(font)
            self.slot_labels.append(lbl)
            self.slots_layout.addWidget(lbl)

    def start_round(self, player_name: str, category: str, difficulty: str, word: str):
        self.player_name = player_name
        self.category = category
        self.difficulty = difficulty
        self.current_word = word.upper()
        self.word_set = set(self.current_word)
        self.state = GameState(self.current_word)

        self.lbl_player.setText(f"Player: {self.player_name}")
        self.lbl_cat.setText(f"Category: {self.category}")
        self.lbl_diff.setText(f"Difficulty: {self.difficulty}")

        self.reset_round(keep_word=True)

    def reset_round(self, keep_word: bool = True):
        if self.state is None:
            return
        if not keep_word:
            self.state = GameState(self.current_word)

        self.lbl_msg.setText("Pick a letter to begin")

        for b in self.key_buttons.values():
            b.setEnabled(True)
            b.setStyleSheet(f"font-size: {F(22)}px; font-weight: 800;")

        self._ensure_slots()
        self._update_all()

    def _update_all(self):
        if self.state is None:
            return

        for i, ch in enumerate(self.state.word):
            lbl = self.slot_labels[i]
            if ch in self.state.revealed:
                lbl.setText(ch)
                lbl.setStyleSheet(self._style_slot_revealed + f" font-size: {F(28)}px;")
            else:
                lbl.setText("_")
                lbl.setStyleSheet("")

        size = S(14)
        for i, dot in enumerate(self.life_dots):
            if i < self.state.life:
                dot.setStyleSheet(f"background-color: rgba(248,250,252,0.92); border-radius: {size//2}px;")
            else:
                dot.setStyleSheet(f"background-color: rgba(248,250,252,0.18); border-radius: {size//2}px;")

        self.lbl_preview.setText("  ".join([c if c in self.state.revealed else "_" for c in self.state.word]))
        self.lbl_wrong.setText("Wrong: " + ", ".join(sorted(self.state.wrong)))
        self.lbl_lives.setText(f"Lives: {self.state.life}")
        self.lbl_score.setText(f"Score: {self.state.score}")

        if self.state.is_won() or self.state.is_lost():
            res = self.state.finish_round()
            self.round_finished.emit(res)

    def guess(self, letter: str):
        if self.state is None:
            return
        letter = letter.upper()
        if letter not in self.key_buttons:
            return
        btn = self.key_buttons[letter]
        if not btn.isEnabled():
            return

        ok = self.state.guess(letter)
        btn.setDisabled(True)

        if ok:
            self.lbl_msg.setText(f"Nice! {letter} is in the word.")
            btn.setStyleSheet(self._style_key_correct + f" font-size: {F(22)}px;")
        else:
            self.lbl_msg.setText(f"Oops! {letter} is not in the word.")
            btn.setStyleSheet(self._style_key_wrong + f" font-size: {F(22)}px;")

        self._update_all()

    def use_hint(self):
        if self.state is None:
            return
        used = self.state.use_hint()
        if not used:
            self.lbl_msg.setText("Not enough points for a hint!")
            return
        self.lbl_msg.setText("Hint used.")
        for ch in list(self.state.revealed):
            if ch in self.key_buttons:
                self.key_buttons[ch].setDisabled(True)
        self._update_all()

    def handle_physical_key(self, key: int, text: str):
        if self.state is None:
            return
        if not text:
            return
        ch = text.upper()
        if len(ch) != 1:
            return
        if ch < "A" or ch > "Z":
            return
        self.guess(ch)


class ResultScreen(QWidget):
    next_round = pyqtSignal()
    back_menu = pyqtSignal()

    def __init__(self):
        super().__init__()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(S(60), S(50), S(60), S(50))
        outer.addStretch()

        row = QHBoxLayout()
        row.addStretch()

        self.card = GlassCard()
        self.card.setMinimumWidth(S(720))
        self.card.setMaximumWidth(S(980))

        lay = QVBoxLayout(self.card)
        lay.setContentsMargins(S(56), S(44), S(56), S(44))
        lay.setSpacing(S(16))

        self.lbl_title = QLabel("You Win!")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setFont(QFont("Segoe UI", F(44), QFont.Bold))

        self.lbl_word = QLabel("Word: -")
        self.lbl_word.setAlignment(Qt.AlignCenter)
        self.lbl_word.setFont(QFont("Segoe UI", F(18), QFont.DemiBold))
        self.lbl_word.setStyleSheet("color: rgba(248,250,252,0.82);")

        self.lbl_score = QLabel("Round Score: 0")
        self.lbl_score.setAlignment(Qt.AlignCenter)
        self.lbl_score.setFont(QFont("Segoe UI", F(18), QFont.DemiBold))
        self.lbl_score.setStyleSheet("color: rgba(248,250,252,0.82);")

        actions = QHBoxLayout()
        actions.setSpacing(S(14))

        self.btn_next = QPushButton("Next Round")
        self.btn_next.setObjectName("PrimaryButton")
        self.btn_next.setFixedHeight(S(60))
        self.btn_next.setFont(QFont("Segoe UI", F(16), QFont.Bold))
        self.btn_next.clicked.connect(self.next_round.emit)

        self.btn_menu = QPushButton("Menu")
        self.btn_menu.setObjectName("GhostButton")
        self.btn_menu.setFixedHeight(S(60))
        self.btn_menu.setFont(QFont("Segoe UI", F(16), QFont.Bold))
        self.btn_menu.clicked.connect(self.back_menu.emit)

        actions.addWidget(self.btn_next, 1)
        actions.addWidget(self.btn_menu, 1)

        lay.addWidget(self.lbl_title)
        lay.addSpacing(S(4))
        lay.addWidget(self.lbl_word)
        lay.addWidget(self.lbl_score)
        lay.addSpacing(S(10))
        lay.addLayout(actions)

        row.addWidget(self.card)
        row.addStretch()

        outer.addLayout(row)
        outer.addStretch()

    def set_result(self, won: bool, word: str, round_score: int):
        self.lbl_title.setText("You Win!" if won else "Game Over")
        color = "#4ADE80" if won else "#EF4444"
        self.lbl_title.setStyleSheet(f"color: {color};")
        self.lbl_word.setText(f"Word: {word}")
        self.lbl_score.setText(f"Round Score: {round_score}")


class BackgroundLayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.label = QLabel(self)
        self.label.setScaledContents(False)
        self.pix_light = QPixmap()
        self.pix_dark = QPixmap()
        self._dark = False

    def set_images(self, light_path: str, dark_path: str):
        self.pix_light = QPixmap(light_path)
        self.pix_dark = QPixmap(dark_path)
        self._apply()

    def set_dark(self, dark: bool):
        self._dark = bool(dark)
        self._apply()

    def _apply(self):
        pix = self.pix_dark if self._dark else self.pix_light
        if pix.isNull():
            self.label.setPixmap(QPixmap())
            return
        self.label.setPixmap(fit_cover(pix, self.size()))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.label.setGeometry(0, 0, self.width(), self.height())
        self._apply()


class MainWindow(QMainWindow):
    def __init__(self, categories):
        super().__init__()
        self.setWindowTitle("Word-Maze")

        self._dark = False
        self._player_name = ""
        self._category = ""
        self._difficulty = ""

        self.words_file = data_path("words.json")
        self.save_file = data_path("save_data.json")

        self.bg = BackgroundLayer(self)
        self.bg.setGeometry(0, 0, 1, 1)
        self.bg.set_images(
            assets_path("assets", "Background", "BACK.jpg"),
            assets_path("assets", "Background", "BACKdark.jpg")
        )

        self.stack = QStackedWidget()
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(self.stack)
        self.setCentralWidget(root)

        self.menu = MainMenuScreen(categories)
        self.game = GameScreen()
        self.result = ResultScreen()

        self.stack.addWidget(self.menu)
        self.stack.addWidget(self.game)
        self.stack.addWidget(self.result)

        self.menu.start_game_signal.connect(self._start_game)
        self.game.round_finished.connect(self._round_finished)
        self.game.go_menu.connect(self._back_to_menu)
        self.result.next_round.connect(self._next_round)
        self.result.back_menu.connect(self._back_to_menu)

        self.exit_btn = QPushButton("✕", self)
        self.exit_btn.setObjectName("ExitButton")
        self.exit_btn.setFixedSize(S(44), S(44))
        self.exit_btn.setFont(QFont("Segoe UI", F(14), QFont.Bold))
        self.exit_btn.clicked.connect(QApplication.instance().quit)

        self._progress = load_progress(self.save_file)

    def set_dark_mode(self, dark: bool):
        self._dark = bool(dark)
        self.bg.set_dark(self._dark)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.bg.setGeometry(0, 0, self.width(), self.height())
        m = S(18)
        self.exit_btn.setFixedSize(S(44), S(44))
        self.exit_btn.move(self.width() - self.exit_btn.width() - m, m)

    def keyPressEvent(self, event):
        if self.stack.currentWidget() == self.game:
            self.game.handle_physical_key(event.key(), event.text())
        super().keyPressEvent(event)

    def _start_game(self, player_name: str, category: str, difficulty: str):
        self._player_name = player_name
        self._category = category
        self._difficulty = difficulty

        if player_name.strip().lower() == "ayla":
            dlg = AylaDialog(self)
            dlg.proceed.connect(lambda: self._start_game_after_dialog(category, difficulty))
            dlg.exec_()
        else:
            self._start_game_after_dialog(category, difficulty)

    def _start_game_after_dialog(self, category: str, difficulty: str):
        word = word_loader.pick_word(category)
        self.game.start_round(self._player_name, category, difficulty, word)
        self.stack.setCurrentWidget(self.game)

    def _round_finished(self, result: dict):
        done = update_progress(self.save_file, result)
        self._progress = done
        won = bool(result.get("won"))
        round_score = int(result.get("round_score", 0))
        word = self.game.state.word if self.game.state else ""
        self.result.set_result(won, word, round_score)
        self.stack.setCurrentWidget(self.result)

    def _next_round(self):
        word = word_loader.pick_word(self._category)
        self.game.start_round(self._player_name, self._category, self._difficulty, word)
        self.stack.setCurrentWidget(self.game)

    def _back_to_menu(self):
        self.stack.setCurrentWidget(self.menu)


def _compute_ui_scale(app: QApplication, max_word_len: int) -> float:
    screen = app.primaryScreen()
    sw = screen.size().width()
    sh = screen.size().height()

    BASE_MARGIN = 60
    BASE_MAIN_SPACING = 26
    BASE_LEFT_CARD_W = 420

    BASE_KEY_SIZE = 72
    BASE_KEY_HSP = 12
    KEY_COLS = 10
    base_keyboard_w = KEY_COLS * BASE_KEY_SIZE + (KEY_COLS - 1) * BASE_KEY_HSP

    BASE_SLOT_SIZE = 76
    BASE_SLOT_SP = 12
    base_slots_w = max_word_len * BASE_SLOT_SIZE + max(0, (max_word_len - 1)) * BASE_SLOT_SP

    base_right_min_w = max(base_keyboard_w, base_slots_w)
    required_w = (2 * BASE_MARGIN) + BASE_MAIN_SPACING + BASE_LEFT_CARD_W + base_right_min_w
    required_h = BASE_HEIGHT

    scale = min(sw / required_w, sh / required_h)
    scale *= 0.92
    return max(0.55, min(scale, 1.55))


def run():
    app = QApplication(sys.argv)

    words_file = data_path("words.json")
    with open(words_file, "r", encoding="utf-8") as f:
        data = __import__("json").load(f)

    categories = sorted(list(data.keys()))
    all_words = []
    for k in categories:
        for w in data.get(k, []):
            if isinstance(w, str) and w.strip():
                all_words.append(w.strip())

    max_word_len = max([len(w) for w in all_words], default=8)

    global UI_SCALE
    UI_SCALE = _compute_ui_scale(app, max_word_len)

    base_font = QFont("Segoe UI", F(12))
    base_font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(base_font)
    app.setStyleSheet(STYLESHEET)

    word_loader.load(words_file)

    win = MainWindow(categories)

    screen = app.primaryScreen()
    size = screen.size()
    win.resize(size.width(), size.height())

    if GlobalBlur is not None:
        try:
            GlobalBlur(win.winId(), Dark=True, Acrylic=True)
        except Exception:
            pass

    win.showFullScreen()
    sys.exit(app.exec_())
