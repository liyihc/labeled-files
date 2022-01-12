from __future__ import annotations
from os import stat
import random
import shutil
from dataclasses import dataclass
from datetime import datetime
import pydantic
import enum
from functools import partial, reduce
import pathlib
import sqlite3
from typing import Dict, List, Set, Union

from .fileUiPy import File, Window as FileWin

from PySide6 import QtCore, QtGui, QtWidgets

from .mainUi import Ui_MainWindow

SQLITE_NAME = "LABELED_FILES.sqlite3"


class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.setting = Setting()

        config_path = pathlib.Path("config.json")
        if config_path.exists():
            self.config = Config.parse_file(config_path)
        else:
            self.config = Config()

        self.menu.addSeparator()
        for space, path in self.config.workspaces.items():
            action = QtGui.QAction(space, self)
            action.triggered.connect(partial(self.setting.set_root, path))
            self.menu.addAction(action)

        self.table = FileTable(self.setting, self)
        self.fileVerticalLayout.addWidget(self.table)

        self.searchPushButton.clicked.connect(self.search)
        self.openWorkSpaceAction.triggered.connect(self.open_workspace)

        default = self.config.workspaces.get(self.config.default, None)
        if default:
            self.setting.set_root(default)

    def open_workspace(self):
        ret = QtWidgets.QFileDialog.getExistingDirectory(
            caption="open a folder as workspace")
        if ret:
            self.setting.set_root(ret)

    def search(self):
        conn = self.setting.conn
        keywords = self.searchLineEdit.text().split()
        if len(keywords):
            file_ids = reduce(lambda a, b: a & b, map(
                lambda kw: {v for v, in conn.execute("SELECT file_id FROM file_labels WHERE label = ?", (kw,))}, keywords))
        else:
            file_ids = [f for f, in conn.execute(
                "SELECT id FROM files ORDER BY ctime desc LIMIT 50")]
        file_ids = ','.join(str(f) for f in file_ids)

        def get_file(args):
            id, name, path, ctime, _, description = args
            path = pathlib.Path(path)
            if not path.is_absolute():
                path = self.root_path.joinpath(path)
            tags = [tag for tag, in conn.execute(
                "SELECT label FROM file_labels WHERE file_id = ?", (id,))]
            return File(id, name, str(path), tags, datetime.fromisoformat(ctime), datetime.fromtimestamp(path.stat().st_mtime), description)

        files: List[File] = list(map(get_file, conn.execute(
            f"SELECT * FROM files WHERE id in ({file_ids})")))

        files.sort(key=lambda f: f.mtime, reverse=True)
        self.table.showFiles(files)

    def __del__(self):
        conn = self.setting.conn
        if conn:
            conn.commit()
            conn.close()


class FileTable(QtWidgets.QTableWidget):

    def __init__(self, setting: Setting, parent=None) -> None:
        super().__init__(parent)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setAcceptDrops(True)
        self.setSortingEnabled(False)
        self.verticalHeader().setHidden(True)
        self.horizontalHeader().setStretchLastSection(True)

        self.setHorizontalScrollMode(
            QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["文件名", "时间", "修改时间", "标签", "描述"])
        h = self.horizontalHeader()
        for i, size in enumerate([200, 120, 100]):
            h.resizeSection(i, size)

        self.files: List[File] = []
        self.itemDoubleClicked.connect(self.open_file)
        self.wins = []
        self.setting = setting

    def showFiles(self, results: List[File]):
        self.clearContents()
        self.setRowCount(0)
        self.files = results
        self.setRowCount(len(results))
        icon_provider = QtWidgets.QFileIconProvider()
        for row, file in enumerate(results):
            p = QtCore.QFileInfo(file.path)
            icon = icon_provider.icon(p)
            item = QtWidgets.QTableWidgetItem(icon, file.name)
            self.setItem(row, 0, item)
            self.setItem(row, 1, QtWidgets.QTableWidgetItem(
                file.ctime.strftime("%y%m%d %H:%M:%S")))
            self.setItem(row, 2, QtWidgets.QTableWidgetItem(
                file.mtime.strftime("%y%m%d %H:%M:%S")))
            self.setItem(row, 3, QtWidgets.QTableWidgetItem(
                ' '.join('#' + tag for tag in file.tags)))
            self.setItem(row, 4, QtWidgets.QTableWidgetItem(file.description))

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        # 或者图片、在线文件也可进行下载
        data = event.mimeData()
        text = data.text().splitlines()
        if text and text[0].startswith("file:///"):
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

        match e.dropAction():
            case QtCore.Qt.DropAction.MoveAction:
                def func(p: pathlib.Path):
                    while True:
                        target_p = self.setting.root_path.joinpath(
                            f"{p.stem} {datetime.now().strftime('%y-%m-%d %H_%M_%S')} {format(random.randint(0,9999), '05d')}{p.suffix}")
                        if not target_p.exists():
                            break
                    shutil.move(p, target_p)
                    return target_p

            case QtCore.Qt.DropAction.CopyAction:
                def func(p: pathlib.Path):
                    while True:
                        target_p = self.setting.root_path.joinpath(
                            f"{p.stem} {datetime.now().strftime('%y-%m-%d %H_%M_%S')} {format(random.randint(0,9999), '05d')}{p.suffix}")
                        if not target_p.exists():
                            break
                    if p.is_dir():
                        shutil.copytree(p, target_p)
                    else:
                        shutil.copy(p, target_p)
                    return target_p
            case QtCore.Qt.DropAction.LinkAction:
                def func(p):
                    return p

        for file in e.mimeData().text().splitlines():
            p = pathlib.Path(file.removeprefix("file:///"))
            stat = p.stat()
            f = File(None, p.name, None, [], datetime.fromtimestamp(
                stat.st_ctime), datetime.fromtimestamp(stat.st_mtime), "")
            p = func(p)
            f.path = str(p)
            cur = self.setting.conn.execute(
                f"INSERT INTO files(name, path, ctime, mtime, description) VALUES(?,?,?,?,?)",
                (f.name, f.path, str(f.ctime), str(f.mtime), f.description))

        e.ignore()

    def contextMenuEvent(self, e: QtGui.QContextMenuEvent) -> None:
        item = self.itemAt(e.pos())
        if not item:
            e.ignore()
            return
        menu = QtWidgets.QMenu(self)
        open = QtGui.QAction('open', self)
        open.triggered.connect(lambda: self.open_file(item))
        edit = QtGui.QAction('edit', self)
        edit.triggered.connect(
            lambda: self.edit_file(item)
        )
        menu.addActions([open, edit])
        menu.popup(e.globalPos())

    def open_file(self, item: QtWidgets.QTableWidgetItem):
        return QtGui.QDesktopServices.openUrl(
            QtCore.QUrl.fromLocalFile(self.files[item.row()].path))

    def edit_file(self, item: QtWidgets.QTableWidgetItem):
        win = FileWin(self.setting, self.files[item.row()])
        win.confirmed.connect(self.confirm_file)
        win.show()
        self.wins.append(win)

    def confirm_file(self, file: File):
        conn = self.setting.conn
        conn.execute(
            "UPDATE files SET name = ?, path = ?, ctime = ?, description = ? WHERE id = ?", (file.name, file.path, str(file.ctime), file.description, file.id))
        tags = set(tag for tag, in conn.execute(
            "SELECT label FROM file_labels WHERE file_id = ?", (file.id,)))
        new_tags = set(file.tags)
        if tags != new_tags:
            conn.executemany(
                "INSERT INTO file_labels(file_id, label) VALUES(?,?)",
                [(file.id, tag) for tag in new_tags - tags])
            conn.executemany(
                "DELETE FROM file_labels WHERE file_id = ? AND label = ?",
                [(file.id, tag) for tag in tags - new_tags])


@dataclass
class Setting:
    root_path: pathlib.Path = None
    conn: sqlite3.Connection = None

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
    ctime DATETIME,
    mtime DATETIME,
    description TEXT);
CREATE INDEX IF NOT EXISTS files_name
    ON files(name);
CREATE INDEX IF NOT EXISTS files_ctime
    ON files(ctime); 
CREATE INDEX IF NOT EXISTS files_mtime
    ON files(mtime); """)
        self.conn = conn

    def set_root(self, root: str):
        if self.conn:
            self.conn.close()
        self.root_path = pathlib.Path(root)
        self.connect_to(self.root_path.joinpath(SQLITE_NAME))


class Config(pydantic.BaseModel):
    default: str = ""
    workspaces: Dict[str, pydantic.DirectoryPath] = {}
