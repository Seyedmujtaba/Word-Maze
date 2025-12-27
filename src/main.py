import sys
from PyQt5.QtWidgets import QApplication

from .main_window import run


def main():
    app = QApplication(sys.argv)
    window = run()
    if window is not None:
        window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
