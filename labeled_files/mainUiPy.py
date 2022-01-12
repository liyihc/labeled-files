import pathlib
import sqlite3

from PySide6 import QtCore, QtGui, QtWidgets

from .mainUi import Ui_MainWindow

SQLITE_NAME = "LABELED_FILES.sqlite3"


class ListView(QtWidgets.QListView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        # 或者图片、在线文件也可进行下载
        text = event.mimeData().text()
        if text.startswith('file:///'):
            event.accept()

    def dragMoveEvent(self, e: QtGui.QDragMoveEvent) -> None:
        if e.pos().y() < self.pos().y() + self.height() / 2:
            # 如果不是文件，则不要accept
            e.setDropAction(QtCore.Qt.DropAction.MoveAction)
        else:
            e.setDropAction(QtCore.Qt.DropAction.CopyAction)

    def dropEvent(self, e: QtGui.QDropEvent) -> None:
        self.dragMoveEvent(e)
        match e.dropAction():
            case QtCore.Qt.DropAction.MoveAction:
                print("mv", e.mimeData().text())
            case QtCore.Qt.DropAction.CopyAction:
                print("cp", e.mimeData().text())
        e.accept()


class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        self.listview = ListView(self)
        self.listVerticalLayout.addWidget(self.listview)

        self.openWorkSpaceAction.triggered.connect(self.open_workspace)

        self.root_path: pathlib.Path = None
        self.sqlite_conn: sqlite3.Connection = None

    def open_workspace(self):
        ret = QtWidgets.QFileDialog.getExistingDirectory(
            caption="open a folder as workspace")
        if ret:
            if self.sqlite_conn:
                self.sqlite_conn.close()
            self.root_path = pathlib.Path(ret)
            self.sqlite_conn = sqlite_connect(self.root_path)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self.sqlite_conn:
            self.sqlite_conn.close()
        event.accept()


def sqlite_connect(root_path: pathlib.Path):
    conn = sqlite3.connect(root_path.joinpath(SQLITE_NAME))
    conn.executescript("""
CREATE TABLE IF NOT EXISTS file_labels(
    label TEXT,
    file_name TEXT,
    PRIMARY KEY(file_name, label));
CREATE INDEX IF NOT EXISTS file_labels_label
    ON file_labels(label, file_name);
CREATE TABLE IF NOT EXISTS files(
    name TEXT,
    path TEXT,
    mtime DATETIME,
    description TEXT);
CREATE INDEX IF NOT EXISTS files_name
    ON files(name);
CREATE INDEX IF NOT EXISTS files_mtime
    ON files(mtime); """)
    return conn
