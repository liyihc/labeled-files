from __future__ import annotations
from datetime import datetime
import enum
from functools import reduce
import pathlib
import sqlite3
from typing import List, NamedTuple, Union

from PySide6 import QtCore, QtGui, QtWidgets

from .mainUi import Ui_MainWindow

SQLITE_NAME = "LABELED_FILES.sqlite3"


class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        self.table = FileTable(self)
        self.fileVerticalLayout.addWidget(self.table)

        self.table.drop.connect(self.dropped)
        self.searchPushButton.clicked.connect(self.search)
        self.openWorkSpaceAction.triggered.connect(self.open_workspace)

        self.root_path: pathlib.Path = None
        self.conn: sqlite3.Connection = None
        self.connect_to(":memory:")

    def connect_to(self, path: Union[str, pathlib.Path]):
        conn = sqlite3.connect(path)
        conn.executescript("""
CREATE TABLE IF NOT EXISTS file_labels(
    label TEXT,
    file_id INTEGER,
    PRIMARY KEY(file_id, label));
CREATE INDEX IF NOT EXISTS file_labels_label
    ON file_labels(label, file_id);
CREATE TABLE IF NOT EXISTS files(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    path TEXT,
    mtime DATETIME,
    description TEXT);
CREATE INDEX IF NOT EXISTS files_name
    ON files(name);
CREATE INDEX IF NOT EXISTS files_mtime
    ON files(mtime); """)
        self.conn = conn

    def open_workspace(self):
        ret = QtWidgets.QFileDialog.getExistingDirectory(
            caption="open a folder as workspace")
        if ret:
            if self.sqlite_conn:
                self.sqlite_conn.close()
            self.root_path = pathlib.Path(ret)
            self.files.setSqlite(self.root_path.joinpath(SQLITE_NAME))

    def dropped(self, drop_action: QtCore.Qt.DropAction, urls: List[QtCore.QUrl]):
        match drop_action:
            case QtCore.Qt.DropAction.MoveAction:
                pass
            case QtCore.Qt.DropAction.CopyAction:
                pass
            case QtCore.Qt.DropAction.LinkAction:
                def func(url: QtCore.QUrl):
                    p = pathlib.Path(url.toLocalFile())
                    cur = self.conn.execute(
                        f"INSERT INTO files(name, path, mtime, description) VALUES(?,?,?,?)",
                        (p.name, str(p), str(datetime.fromtimestamp(p.stat().st_mtime)), ""))
                    cur.lastrowid
        list(map(func, urls))

    def search(self):
        keywords = self.searchLineEdit.text().split()
        if len(keywords):
            file_ids = reduce(lambda a, b: a & b, map(
                lambda kw: {v for v, in self.conn.execute("SELECT file_id FROM file_labels WHERE label = ?", (kw,))}, keywords))
        else:
            file_ids = list(self.conn.execute(
                "SELECT id FROM files ORDER BY mtime desc LIMIT 50"))
        file_ids = ','.join(str(f) for f, in file_ids)
        conn = self.conn

        def get_file(args):
            id, name, path, _, description = args
            path = pathlib.Path(path)
            if not path.is_absolute():
                path = self.root_path.joinpath(path)
            tags = list(conn.execute(
                "SELECT label FROM file_labels WHERE file_id = ?", (id,)))
            return File(id, name, str(path), tags, datetime.fromtimestamp(path.stat().st_mtime), description)

        files: List[File] = list(map(get_file, self.conn.execute(
            f"SELECT * FROM files WHERE id in ({file_ids})")))

        files.sort(key=lambda f: f.mtime, reverse=True)
        self.table.showFiles(files)

    def __del__(self):
        if self.conn:
            self.conn.close()


class FileTable(QtWidgets.QTableWidget):
    drop = QtCore.Signal(QtCore.Qt.DropAction, list)

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setAcceptDrops(True)
        self.verticalHeader().setHidden(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.setHorizontalScrollMode(
            QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["文件名", "修改时间", "标签", "描述"])
        h = self.horizontalHeader()
        for i, size in enumerate([200, 120, 100]):
            h.resizeSection(i, size)

    def showFiles(self, results: List[File]):
        self.clearContents()
        self.setRowCount(0)
        self.setRowCount(len(results))
        icon_provider = QtWidgets.QFileIconProvider()
        for row, file in enumerate(results):
            p = QtCore.QFileInfo(file.path)
            icon = icon_provider.icon(p)
            item = QtWidgets.QTableWidgetItem(icon, file.name)
            self.setItem(row, 0, item)
            self.setItem(row, 1, QtWidgets.QTableWidgetItem(
                file.mtime.strftime("%y%m%d %H:%M:%S")))
            self.setItem(row, 2, QtWidgets.QTableWidgetItem(
                ' '.join(file.tags)))
            self.setItem(row, 3, QtWidgets.QTableWidgetItem(file.description))

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        # 或者图片、在线文件也可进行下载
        data = event.mimeData()
        if data.hasUrls():
            print(data.urls())
            url = data.urls()[0]
            if url.isLocalFile():
                event.accept()

    def dragMoveEvent(self, e: QtGui.QDragMoveEvent) -> None:
        if e.pos().y() < self.height() / 2:
            if e.pos().x() < self.width() / 2:
                # 如果不是文件，则不要accept，因为这是move
                e.setDropAction(QtCore.Qt.DropAction.MoveAction)
            else:
                # 如果是在线数据，需要拒绝
                e.setDropAction(QtCore.Qt.DropAction.CopyAction)
        else:
            # 如果是在线数据，需要拒绝
            e.setDropAction(QtCore.Qt.DropAction.LinkAction)

    def dropEvent(self, e: QtGui.QDropEvent) -> None:
        self.dragMoveEvent(e)
        self.drop.emit(e.dropAction(), e.mimeData().urls())
        e.ignore()


class File(NamedTuple):
    id: int
    name: str
    path: str
    tags: List[str]
    mtime: datetime
    description: str
