import multiprocessing

multiprocessing.freeze_support()

if __name__ == "__main__":
    try:
        # os.environ.pop("QT_PLUGIN_PATH", None)
        from PySide6 import QtWidgets
        from labeled_files.mainUiPy import Window
        app = QtWidgets.QApplication([])
        win = Window()
        win.show()
        win.config_init()
        win.search()
        import sys
        sys.exit(app.exec())
    except Exception as e:
        import logging
        logger = logging.getLogger("exception")
        logger.exception(e)
