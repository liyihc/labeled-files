from PySide6 import QtWidgets
import sys
import logging
from labeled_files.mainUiPy import Window

logger = logging.getLogger("exception")

formatter = logging.Formatter(
    "\n%(asctime)s - %(filename)s - %(levelname)s \n %(message)s")
log_file_handler = logging.FileHandler('exception.txt', encoding='utf-8')
log_file_handler.setFormatter(formatter)
logger.addHandler(log_file_handler)
logger.setLevel(logging.DEBUG)


def main():
    app = QtWidgets.QApplication([])
    win = Window()
    win.show()
    win.search()
    return app


if __name__ == "__main__":
    app = main()
    sys.exit(app.exec())
