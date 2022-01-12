import sys
from PySide6 import QtWidgets, QtCore, QtGui


class MyWidget(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.setLayout(QtWidgets.QVBoxLayout(self))

        self.btn = QtWidgets.QPushButton("Click me")
        self.btn.clicked.connect(self.set_text)
        self.txt = QtWidgets.QLabel("HW")
        self.layout().addWidget(self.txt)
        self.layout().addWidget(self.btn)

    def set_text(self):
        self.txt.setText("ccc")


if __name__ == "__main__":
    app = QtWidgets.QApplication()

    w = MyWidget()
    w.show()
    sys.exit(app.exec())
