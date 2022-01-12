import sys
from PySide6 import QtWidgets, QtCore, QtGui


class MyWidget(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setLayout(QtWidgets.QVBoxLayout(self))

        model = QtWidgets.QFileSystemModel()
        model.setRootPath(QtCore.QDir.currentPath())
        tree = QtWidgets.QTreeView()
        tree.setModel(model)

        tree.setRootIndex(model.index(QtCore.QDir.currentPath()))
        self.layout().addWidget(tree)


if __name__ == "__main__":
    app = QtWidgets.QApplication()

    w = MyWidget()
    w.show()
    sys.exit(app.exec())
