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
from .progress_manager import load_progress, update_progress

try:
    from BlurWindow.blurWindow import GlobalBlur
except Exception:
    GlobalBlur = None


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


def repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(here, ".."))


def assets_path(*parts: str) -> str:
    return os.path.join(repo_root(), *parts)


def data_path(*parts: str) -> str:
    return os.path.join(repo_root(), "data", *parts)


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
QMainWindow { background: transparent; }

QLabel {
    color: rgba(248, 250, 252, 0.92);
    font-family: 'Segoe UI', sans-serif;
}

QFrame#GlassCard {
    background-color: rgba(15, 23, 42, 0.60);
    border: 1px solid rgba(255, 255, 255, 0.28);
    border-radius: 30px;
}

QLabel#MenuSubtitle { color: rgba(248, 250, 252, 0.72); }
QLabel#MenuFieldLabel { color: rgba(248, 250, 252, 0.82); }
QLabel#MenuFooter { color: rgba(248, 250, 252, 0.55); }

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
    font-weight: 800;
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
        lay.setContentsMargins(S(40), S(34), S(40), S(30))
        lay.setSpacing(S(18))

        title = QLabel("Message")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", F(20), QFont.Bold))

        msg = QLabel("mujtaba loves you Ayla")
        msg.setWordWrap(True)
        msg.setAlignment(Qt.AlignCenter)
        msg.setFont(QFont("Segoe UI", F(16), QFont.DemiBold))

        btn = QPushButton("Start")
        btn.setObjectName("PrimaryButton")
        btn.setFixedHeight(S(56))
        btn.setFont(QFont("Segoe UI", F(16), QFont.Bold))
        btn.clicked.connect(self._go)

        lay.addWidget(title)
        lay.addWidget(msg)
        lay.addSpacing(S(6))
        lay.addWidget(btn)

        outer.addWidget(card)

        self.setFixedSize(S(560), S(280))

    def _go(self):
        self.accept()
        self.proceed.emit()


class MainMenuScreen(QWidget):
    start_game_signal = pyqtSignal(str, str, str)
    theme_toggled = pyqtSignal(bool)

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
        self.menu_card.setMaximumWidth(S(1180))

        card_layout = QVBoxLayout(self.menu_card)
        card_layout.setContentsMargins(S(56), S(46), S(56), S(46))
        card_layout.setSpacing(S(18))

        top_row = QHBoxLayout()
        top_row.addStretch()

        self.btn_theme = QPushButton("Dark Mode")
        self.btn_theme.setObjectName("ThemeButton")
        self.btn_theme.setFixedHeight(S(52))
        self.btn_theme.setFixedWidth(S(220))
        self.btn_theme.setFont(QFont("Segoe UI", F(15), QFont.Bold))
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
        self.input_name.setFixedHeight(S(52))
        self.input_name.setFont(QFont("Segoe UI", F(14)))
        self.input_name.textChanged.connect(self._validate)

        label_cat = QLabel("Category")
        label_cat.setObjectName("MenuFieldLabel")
        label_cat.setFont(QFont("Segoe UI", F(13), QFont.DemiBold))

        self.category_combo = QComboBox()
        self.category_combo.addItems(self.categories)
        self.category_combo.setFixedHeight(S(52))
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
            b.setFixedHeight(S(52))
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
        self.btn_play.setFixedHeight(S(60))
        self.btn_play.setFont(QFont("Segoe UI", F(16), QFont.Bold))
        self.btn_play.clicked.connect(self._play)

        self.btn_quit = QPushButton("Quit")
        self.btn_quit.setObjectName("GhostButton")
        self.btn_quit.setFixedHeight(S(60))
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
        self.theme_toggled.emit(self._dark)


class GameScreen(QWidget):
    round_finished = pyqtSignal(dict)
    go_menu = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.player_name = ""
        self.category = ""
        self.difficulty = ""

        self.state = None
        self.key_buttons = {}
        self.slot_labels = []
        self.life_dots = []
        self._slots_cols = None

        self._style_key_correct = (
            "background-color: rgba(191, 219, 254, 0.95);"
            "color: rgba(2, 6, 23, 0.95);"
            "border-radius: 18px;"
            "font-weight: 900;"
        )
        self._style_key_wrong = (
            "background-color: rgba(239, 68, 68, 0.90);"
            "color: rgba(248, 250, 252, 0.95);"
            "border-radius: 18px;"
            "font-weight: 900;"
        )
        self._style_slot_revealed = (
            "background-color: rgba(248, 250, 252, 0.92);"
            "color: rgba(2, 6, 23, 0.95);"
            "border-radius: 22px;"
            "font-weight: 900;"
        )

        self._build_ui()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.state is None:
            return
        cols = self._compute_slots_per_row()
        if cols != self._slots_cols:
            self._rebuild_slots()
            self._sync_slots()

    def _compute_slots_per_row(self) -> int:
        slot_w = S(90)
        spacing = S(12)
        w = self.slots_container.width()
        if w <= 0:
            w = max(1, self.width() - 2 * S(60))
        cols = int((w + spacing) // (slot_w + spacing))
        return max(1, cols)

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
        left.addWidget(self.lbl_wrong)
        left.addWidget(self.lbl_lives)
        left.addStretch()
        left.addWidget(self.lbl_score)

        right = QVBoxLayout()
        right.setSpacing(S(18))

        self.status_card = GlassCard()
        status = QVBoxLayout(self.status_card)
        status.setContentsMargins(S(32), S(26), S(32), S(26))
        status.setSpacing(S(10))

        self.lbl_title = QLabel("Guess The Word")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setFont(QFont("Segoe UI", F(30), QFont.Bold))

        self.lbl_msg = QLabel("Pick a letter to begin")
        self.lbl_msg.setAlignment(Qt.AlignCenter)
        self.lbl_msg.setStyleSheet(f"font-size: {F(13)}px; color: rgba(248,250,252,0.75);")

        status.addWidget(self.lbl_title)
        status.addWidget(self.lbl_msg)

        self.slots_container = QWidget()
        self.slots_layout = QVBoxLayout(self.slots_container)
        self.slots_layout.setContentsMargins(0, 0, 0, 0)
        self.slots_layout.setSpacing(S(12))
        self.slots_layout.setAlignment(Qt.AlignCenter)

        self.lives_container = QWidget()
        self.lives_layout = QHBoxLayout(self.lives_container)
        self.lives_layout.setContentsMargins(0, 0, 0, 0)
        self.lives_layout.setSpacing(S(10))
        self.lives_layout.setAlignment(Qt.AlignCenter)

        keyboard_card = GlassCard()
        keyboard = QGridLayout(keyboard_card)
        keyboard.setContentsMargins(S(28), S(24), S(28), S(24))
        keyboard.setSpacing(S(12))

        rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        start_cols = [0, 1, 2]
        key_font = QFont("Segoe UI", F(26), QFont.Bold)
        for r, letters in enumerate(rows):
            c0 = start_cols[r]
            for i, letter in enumerate(letters):
                btn = QPushButton(letter)
                btn.setObjectName("KeyButton")
                btn.setFixedSize(S(70), S(70))
                btn.setFont(key_font)
                btn.setStyleSheet(f"font-size: {F(26)}px; font-weight: 900;")
                btn.setCursor(Qt.PointingHandCursor)
                btn.clicked.connect(lambda checked, l=letter: self.make_guess(l))
                keyboard.addWidget(btn, r, c0 + i)
                self.key_buttons[letter] = btn

        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)
        bottom.setSpacing(S(12))

        self.btn_hint = QPushButton("Hint")
        self.btn_hint.setObjectName("SecondaryButton")
        self.btn_hint.setFixedHeight(S(56))
        self.btn_hint.setFixedWidth(S(150))
        self.btn_hint.setFont(QFont("Segoe UI", F(14), QFont.Bold))
        self.btn_hint.clicked.connect(self.use_hint)

        self.btn_reset = QPushButton("New Word")
        self.btn_reset.setObjectName("GhostButton")
        self.btn_reset.setFixedHeight(S(56))
        self.btn_reset.setFixedWidth(S(170))
        self.btn_reset.setFont(QFont("Segoe UI", F(14), QFont.Bold))
        self.btn_reset.clicked.connect(self.new_word)

        self.btn_menu = QPushButton("Menu")
        self.btn_menu.setObjectName("GhostButton")
        self.btn_menu.setFixedHeight(S(56))
        self.btn_menu.setFixedWidth(S(130))
        self.btn_menu.setFont(QFont("Segoe UI", F(14), QFont.Bold))
        self.btn_menu.clicked.connect(self.go_menu.emit)

        bottom.addWidget(self.btn_hint)
        bottom.addStretch()
        bottom.addWidget(self.btn_reset)
        bottom.addWidget(self.btn_menu)

        right.addWidget(self.status_card)
        right.addWidget(self.slots_container)
        right.addWidget(self.lives_container)
        right.addWidget(keyboard_card)
        right.addLayout(bottom)

        main.addLayout(right, 1)

    def set_round(self, player_name: str, category: str, difficulty: str, word: str):
        self.player_name = player_name
        self.category = category
        self.difficulty = difficulty

        self.lbl_player.setText(f"Player: {player_name}")
        self.lbl_cat.setText(f"Category: {category}")
        self.lbl_diff.setText(f"Difficulty: {difficulty}")

        self.state = GameState(word)
        self._rebuild_slots()
        self._rebuild_lives()
        self._reset_keys()
        self._sync_all()

    def _reset_keys(self):
        for btn in self.key_buttons.values():
            btn.setEnabled(True)
            btn.setStyleSheet(f"font-size: {F(26)}px; font-weight: 900;")

    def _rebuild_slots(self):
        if self.state is None:
            return

        clear_layout(self.slots_layout)
        self.slot_labels = []

        cols = self._compute_slots_per_row()
        self._slots_cols = cols

        row_layout = None
        for i, _ch in enumerate(self.state.word):
            if i % cols == 0:
                row_layout = QHBoxLayout()
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(S(12))
                row_layout.setAlignment(Qt.AlignCenter)
                self.slots_layout.addLayout(row_layout)

            lbl = QLabel("_")
            lbl.setObjectName("LetterSlot")
            lbl.setFixedSize(S(90), S(90))
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFont(QFont("Segoe UI", F(28), QFont.Bold))
            row_layout.addWidget(lbl)
            self.slot_labels.append(lbl)

    def _rebuild_lives(self):
        clear_layout(self.lives_layout)
        self.life_dots = []
        size = S(18)
        for _ in range(self.state.lives):
            dot = QLabel()
            dot.setFixedSize(size, size)
            dot.setStyleSheet(f"background-color: rgba(248, 250, 252, 0.92); border-radius: {size // 2}px;")
            self.lives_layout.addWidget(dot)
            self.life_dots.append(dot)

    def _sync_all(self):
        self._sync_slots()
        self._sync_lives()
        self._sync_preview()
        self._sync_score()

    def _sync_slots(self):
        if self.state is None:
            return
        for i, ch in enumerate(self.state.word):
            lbl = self.slot_labels[i]
            if i in self.state.revealed:
                lbl.setText(ch)
                lbl.setStyleSheet(self._style_slot_revealed + f" font-size: {F(30)}px;")
            else:
                lbl.setText("_")
                lbl.setStyleSheet("")

    def _sync_lives(self):
        if self.state is None:
            return
        size = S(18)
        for i, dot in enumerate(self.life_dots):
            if i < self.state.lives_left:
                dot.setStyleSheet(f"background-color: rgba(248, 250, 252, 0.92); border-radius: {size // 2}px;")
            else:
                dot.setStyleSheet(f"background-color: rgba(248, 250, 252, 0.22); border-radius: {size // 2}px;")
        self.lbl_lives.setText(f"Lives: {self.state.lives_left}")

    def _sync_preview(self):
        if self.state is None:
            return
        self.lbl_preview.setText(self.state.masked())
        wrong = sorted([g for g in self.state.guessed if g not in set(self.state.word)])
        self.lbl_wrong.setText("Wrong: " + ", ".join(wrong))

    def _sync_score(self):
        if self.state is None:
            return
        self.lbl_score.setText(f"Score: {self.state.score}")

    def new_word(self):
        if self.category and self.difficulty:
            self.round_finished.emit({"action": "new_word"})

    def handle_physical_key(self, letter: str):
        if not letter or len(letter) != 1 or not letter.isalpha():
            return
        self.make_guess(letter.upper())

    def make_guess(self, letter: str):
        if self.state is None:
            return
        letter = letter.upper()
        if letter not in self.key_buttons:
            return
        btn = self.key_buttons[letter]
        if not btn.isEnabled():
            return

        result = self.state.guess(letter)
        btn.setDisabled(True)
        if result.get("correct"):
            btn.setStyleSheet(self._style_key_correct + f" font-size: {F(26)}px;")
            self.lbl_msg.setText(f"Nice! {letter} is in the word.")
        elif result.get("already_guessed"):
            self.lbl_msg.setText(f"{letter} already guessed.")
        else:
            btn.setStyleSheet(self._style_key_wrong + f" font-size: {F(26)}px;")
            self.lbl_msg.setText(f"Oops! {letter} is not in the word.")

        self._sync_all()

        if self.state.is_won() or self.state.is_lost():
            payload = self.state.finish_round()
            payload["word"] = self.state.word
            payload["player"] = self.player_name
            payload["category"] = self.category
            payload["difficulty"] = self.difficulty
            self.round_finished.emit(payload)

    def use_hint(self):
        if self.state is None:
            return
        result = self.state.use_hint()
        if result.get("used"):
            self.lbl_msg.setText(f"Hint revealed: {result.get('letter', '')}")
        else:
            if result.get("reason") == "not_enough_score":
                self.lbl_msg.setText("Not enough score for a hint.")
            else:
                self.lbl_msg.setText("Hint not available.")
        self._sync_all()


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
        self.card.setMinimumWidth(S(740))
        self.card.setMaximumWidth(S(980))
        self.card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        lay = QVBoxLayout(self.card)
        lay.setContentsMargins(S(56), S(46), S(56), S(46))
        lay.setSpacing(S(16))

        self.lbl_title = QLabel("Result")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setFont(QFont("Segoe UI", F(42), QFont.Bold))

        self.lbl_word = QLabel("")
        self.lbl_word.setAlignment(Qt.AlignCenter)
        self.lbl_word.setFont(QFont("Segoe UI", F(18), QFont.DemiBold))
        self.lbl_word.setStyleSheet("color: rgba(248, 250, 252, 0.82);")

        self.lbl_score = QLabel("")
        self.lbl_score.setAlignment(Qt.AlignCenter)
        self.lbl_score.setFont(QFont("Segoe UI", F(18), QFont.Bold))

        self.lbl_sub = QLabel("")
        self.lbl_sub.setAlignment(Qt.AlignCenter)
        self.lbl_sub.setWordWrap(True)
        self.lbl_sub.setFont(QFont("Segoe UI", F(13)))
        self.lbl_sub.setStyleSheet("color: rgba(248, 250, 252, 0.72);")

        btns = QHBoxLayout()
        btns.setSpacing(S(12))

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

        btns.addWidget(self.btn_next, 1)
        btns.addWidget(self.btn_menu, 1)

        lay.addWidget(self.lbl_title)
        lay.addWidget(self.lbl_word)
        lay.addWidget(self.lbl_score)
        lay.addWidget(self.lbl_sub)
        lay.addSpacing(S(8))
        lay.addLayout(btns)

        row.addWidget(self.card)
        row.addStretch()

        outer.addLayout(row)
        outer.addStretch()

    def set_result(self, payload: dict):
        won = bool(payload.get("won"))
        word = payload.get("word", "")
        score = int(payload.get("round_score", 0))
        bonus = int(payload.get("bonus", 0))
        mistakes = int(payload.get("mistakes", 0))

        self.lbl_title.setText("You Win!" if won else "Game Over")
        if won:
            self.lbl_title.setStyleSheet(f"color: rgba(74, 222, 128, 0.98); font-size: {F(44)}px; font-weight: 900;")
        else:
            self.lbl_title.setStyleSheet(f"color: rgba(239, 68, 68, 0.98); font-size: {F(44)}px; font-weight: 900;")

        self.lbl_word.setText(f"Word: {word}")
        if bonus > 0:
            self.lbl_score.setText(f"Score: {score} (+{bonus} perfect bonus)")
        else:
            self.lbl_score.setText(f"Score: {score}")

        self.lbl_sub.setText(f"Mistakes: {mistakes}")


class WordMazeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Word-Maze")
        self.setStyleSheet(STYLESHEET)

        self._dark = False
        self._bg_path_light = assets_path("assets", "Background", "BACK.jpg")
        self._bg_path_dark = assets_path("assets", "Background", "BACKdark.jpg")
        self._bg_pix_light = QPixmap(self._bg_path_light)
        self._bg_pix_dark = QPixmap(self._bg_path_dark)

        self._progress_path = data_path("save_data.json")
        self._progress = load_progress(self._progress_path)

        self._player = ""
        self._category = ""
        self._difficulty = ""

        self.bg = QLabel(self)
        self.bg.setScaledContents(False)
        self.bg.setGeometry(0, 0, self.width(), self.height())
        self.bg.lower()

        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

        self.menu = MainMenuScreen(self._categories_pretty())
        self.game = GameScreen()
        self.result = ResultScreen()

        self.stack.addWidget(self.menu)
        self.stack.addWidget(self.game)
        self.stack.addWidget(self.result)

        self.menu.start_game_signal.connect(self._start_game)
        self.menu.theme_toggled.connect(self.set_dark_mode)
        self.game.round_finished.connect(self._on_round_finished)
        self.game.go_menu.connect(self._go_menu)
        self.result.next_round.connect(self._next_round)
        self.result.back_menu.connect(self._go_menu)

        self.exit_btn = QPushButton("✕", self)
        self.exit_btn.setObjectName("ExitButton")
        self.exit_btn.setFixedSize(S(44), S(44))
        self.exit_btn.setFont(QFont("Segoe UI", F(16), QFont.Bold))
        self.exit_btn.setCursor(Qt.PointingHandCursor)
        self.exit_btn.clicked.connect(QApplication.instance().quit)
        self.exit_btn.raise_()

        self._apply_background()

    def _categories_pretty(self):
        cats = word_loader.categories()
        return [c.capitalize() for c in cats]

    def _category_key(self, display: str) -> str:
        return display.strip().lower()

    def _difficulty_key(self, display: str) -> str:
        return display.strip().lower()

    def set_dark_mode(self, enabled: bool):
        self._dark = bool(enabled)
        self._apply_background()
        if GlobalBlur is not None:
            try:
                GlobalBlur(self.winId(), Dark=self._dark, Acrylic=True)
            except Exception:
                pass

    def _apply_background(self):
        pix = self._bg_pix_dark if self._dark else self._bg_pix_light
        target = QSize(max(1, self.width()), max(1, self.height()))
        self.bg.setPixmap(fit_cover(pix, target))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.bg.setGeometry(0, 0, self.width(), self.height())
        self._apply_background()
        margin = S(18)
        self.exit_btn.move(self.width() - self.exit_btn.width() - margin, margin)
        self.exit_btn.raise_()

    def keyPressEvent(self, event):
        if self.stack.currentWidget() is self.game:
            text = event.text()
            if text and len(text) == 1 and text.isalpha():
                self.game.handle_physical_key(text)
                return
        super().keyPressEvent(event)

    def _start_game(self, player: str, category_display: str, difficulty_display: str):
        self._player = player
        self._category = category_display
        self._difficulty = difficulty_display

        if player.strip().lower() == "ayla":
            dlg = AylaDialog(self)
            dlg.proceed.connect(lambda: self._start_game_after_dialog(category_display, difficulty_display))
            dlg.exec_()
            return

        self._start_game_after_dialog(category_display, difficulty_display)

    def _start_game_after_dialog(self, category_display: str, difficulty_display: str):
        cat = self._category_key(category_display)
        diff = self._difficulty_key(difficulty_display)
        word = word_loader.random_word(cat, diff)
        self.game.set_round(self._player, category_display, difficulty_display, word)
        self.stack.setCurrentWidget(self.game)

    def _on_round_finished(self, payload: dict):
        if payload.get("action") == "new_word":
            self._start_game_after_dialog(self._category, self._difficulty)
            return

        update_progress(self._progress_path, payload)
        self.result.set_result(payload)
        self.stack.setCurrentWidget(self.result)

    def _next_round(self):
        self._start_game_after_dialog(self._category, self._difficulty)

    def _go_menu(self):
        self.stack.setCurrentWidget(self.menu)


def _compute_ui_scale(app: QApplication) -> float:
    screen = app.primaryScreen()
    if screen is None:
        return 1.0
    size = screen.size()
    screen_w = float(size.width())
    screen_h = float(size.height())

    base_margin = 60.0
    base_spacing = 26.0
    base_left_w = 420.0

    key_size = 70.0
    key_spacing = 12.0
    key_cols = 10.0
    base_keyboard_w = key_cols * key_size + (key_cols - 1.0) * key_spacing

    words_all = word_loader.words()
    max_len = max([len(w) for w in words_all] + [6])
    max_len = min(max_len, 10)
    slot_size = 90.0
    slot_spacing = 12.0
    base_slots_w = max_len * slot_size + (max_len - 1.0) * slot_spacing

    base_right_min = max(base_keyboard_w, base_slots_w)
    base_required_w = (2.0 * base_margin) + base_spacing + base_left_w + base_right_min
    scale_w = screen_w / base_required_w
    scale_h = screen_h / BASE_HEIGHT
    scale = min(scale_w, scale_h)

    scale *= 0.92
    return max(0.65, min(scale, 1.6))


def run() -> QMainWindow:
    app = QApplication.instance()
    if app is None:
        raise RuntimeError()

    word_loader.load(data_path("words.json"))

    global UI_SCALE
    UI_SCALE = _compute_ui_scale(app)

    base_font = QFont("Segoe UI", F(12))
    base_font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(base_font)

    window = WordMazeWindow()
    if GlobalBlur is not None:
        try:
            GlobalBlur(window.winId(), Dark=True, Acrylic=True)
        except Exception:
            pass

    window.showFullScreen()
    return window
