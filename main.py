from PySide6 import QtWidgets
import sys
import logging

logger = logging.getLogger("exception")

formatter = logging.Formatter(
    "\n%(asctime)s - %(filename)s - %(levelname)s \n %(message)s")
log_file_handler = logging.FileHandler('exception.txt', encoding='utf-8')
log_file_handler.setFormatter(formatter)
logger.addHandler(log_file_handler)
logger.setLevel(logging.DEBUG)

logger = logging.getLogger("record")

formatter = logging.Formatter("%(asctime)s - %(filename)s: %(message)s")
log_file_handler = logging.FileHandler('record.txt', encoding='utf-8')
log_file_handler.setFormatter(formatter)
logger.addHandler(log_file_handler)
logger.setLevel(logging.INFO)


def main():
    from labeled_files.mainUiPy import Window, Config
    from pathlib import Path
    with open(Path(__file__).parent.joinpath('rename-to-config.json'), 'w') as f:
        f.write(Config(
            default="dir1",
            workspaces={
                "dir1":"C:/",
                "dir2":"C:/"
            }
        ).json(indent=4))
    app = QtWidgets.QApplication([])
    win = Window()
    win.show()
    win.search()
    return app


if __name__ == "__main__":
    app = main()
    sys.exit(app.exec())
