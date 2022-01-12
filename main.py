from PySide6 import QtWidgets
import sys
from labeled_files.mainUiPy import Window

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    win = Window()
    win.show()
    sys.exit(app.exec())
