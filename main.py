import logging
import sys


if __name__ == "__main__":
    try:
        from PySide6 import QtWidgets
        from labeled_files.mainUiPy import Window, Config
        from pathlib import Path
        with open(Path(__file__).parent.joinpath('rename-to-config.json'), 'w') as f:
            f.write(Config(
                default="dir1",
                workspaces={
                    "dir1": "C:/",
                    "dir2": "C:/"
                }
            ).json(indent=4))
        app = QtWidgets.QApplication([])
        win = Window()
        win.show()
        win.search()
        sys.exit(app.exec())
    except Exception as e:
        logger = logging.getLogger("exception")
        logger.exception(e)
