import sys
from PyQt5.QtWidgets import QApplication

from .main_window import create_main_window


def main():
    app = QApplication(sys.argv)

    window = create_main_window(app)
    window.showFullScreen()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


