import logging
import sys
import os

if __name__ == "__main__":
    try:
        # os.environ.pop("QT_PLUGIN_PATH", None)
        from PySide6 import QtWidgets
        from labeled_files.mainUiPy import Window, Config
        app = QtWidgets.QApplication([])
        win = Window()
        win.show()
        win.search()
        sys.exit(app.exec())
    except Exception as e:
        logger = logging.getLogger("exception")
        logger.exception(e)
