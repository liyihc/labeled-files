from __future__ import annotations

import os
import pathlib
import random
import shutil
import subprocess
from datetime import datetime
from functools import partial, reduce
from typing import Dict, List, Set, Union

from PySide6 import QtCore, QtGui, QtWidgets

from .fileUiPy import File
from .fileUiPy import Window as FileWin
from .mainUi import Ui_MainWindow
from .setting import SQLITE_NAME, Config, Setting


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

        self.tagLineEdit.keyPressEvent = self.check_complete
        self.setting.lineedits.append(self.tagLineEdit)
        self.table = FileTable(self.setting, self)
        self.fileVerticalLayout.addWidget(self.table)

        self.tagListWidget.itemClicked.connect(self.remove_tag)
        self.searchPushButton.clicked.connect(self.search)
        self.openWorkSpaceAction.triggered.connect(self.open_workspace)
        self.delPushButton.clicked.connect(self.table.del_file)

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
        keyword = self.searchLineEdit.text().strip()
        tags = []
        for i in range(self.tagListWidget.count()):
            tags.append(self.tagListWidget.item(i).text())

        if len(tags):
            file_ids = reduce(lambda a, b: a & b, map(
                lambda tag: {v for v, in conn.execute("SELECT file_id FROM file_labels WHERE label = ?", (tag,))}, tags))
            if keyword:
                file_ids = ','.join(str(f) for f in file_ids)
                file_ids = [f for f, in conn.execute(
                    f'SELECT id FROM files WHERE name like "%{keyword}%" AND id in ({file_ids}) ORDER BY ctime DESC')]
        elif keyword:
            file_ids = [f for f, in conn.execute(
                f'SELECT id FROM files WHERE name like "%{keyword}%" ORDER BY ctime DESC')]
        else:
            file_ids = [f for f, in conn.execute(
                "SELECT id FROM files ORDER BY ctime DESC LIMIT 50")]
        file_ids = ','.join(str(f) for f in file_ids)

        def get_file(args):
            id, name, path, ctime, description = args
            tags = [tag for tag, in conn.execute(
                "SELECT label FROM file_labels WHERE file_id = ?", (id,))]
            return File(id, name, str(path), tags, datetime.fromisoformat(ctime), description)

        files: List[File] = list(map(get_file, conn.execute(
            f"SELECT * FROM files WHERE id in ({file_ids})")))

        self.table.showFiles(files)

    def check_complete(self, e: QtGui.QKeyEvent):
        if self.tagLineEdit.completer() is None:
            self.tagLineEdit.setCompleter(self.setting.completer)
        if e.key() == 32:
            completer = self.tagLineEdit.completer()
            if completer.currentRow() >= 0:
                self.tagListWidget.addItem(QtWidgets.QListWidgetItem(self.style().standardIcon(
                    QtWidgets.QStyle.SP_TitleBarCloseButton), completer.currentCompletion()))
                self.tagLineEdit.setText("")
                e.ignore()
                return
        QtWidgets.QLineEdit.keyPressEvent(self.tagLineEdit, e)

    def remove_tag(self, item: QtWidgets.QListWidgetItem):
        ind = self.tagListWidget.indexFromItem(item)
        self.tagListWidget.takeItem(ind.row())

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
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["文件名", "时间", "标签", "描述"])
        h = self.horizontalHeader()
        for i, size in enumerate([150, 110, 200]):
            h.resizeSection(i, size)

        self.files: List[File] = []
        self.itemDoubleClicked.connect(self.open_file)
        self.wins = []
        self.setting = setting

    def showFiles(self, results: List[File] = None):
        self.clearContents()
        self.setRowCount(0)
        if results is not None:
            self.files = results
        else:
            results = self.files
        self.setRowCount(len(results))
        icon_provider = QtWidgets.QFileIconProvider()
        for row, file in enumerate(results):
            p = pathlib.Path(file.path)
            if not p.is_absolute():
                p = self.setting.root_path.joinpath(p)
            p = QtCore.QFileInfo(p)
            icon = icon_provider.icon(p)
            item = QtWidgets.QTableWidgetItem(icon, file.name)
            self.setItem(row, 0, item)
            self.setItem(row, 1, QtWidgets.QTableWidgetItem(
                file.ctime.strftime("%y%m%d %H:%M:%S")))
            self.setItem(row, 2, QtWidgets.QTableWidgetItem(
                ' '.join('#' + tag for tag in file.tags)))
            self.setItem(row, 3, QtWidgets.QTableWidgetItem(file.description))

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
                    target_p = target_p.relative_to(self.setting.root_path)
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
                    target_p = target_p.relative_to(self.setting.root_path)
                    return target_p
            case QtCore.Qt.DropAction.LinkAction:
                def func(p):
                    return p

        conn = self.setting.conn
        files = []
        for file in e.mimeData().text().splitlines():
            p = pathlib.Path(file.removeprefix("file:///"))
            stat = p.stat()
            f = File(None, p.name, None, [], datetime.fromtimestamp(
                stat.st_ctime), "")
            p = func(p)
            f.path = str(p)
            with conn:
                cur = conn.execute(
                    f"INSERT INTO files(name, path, ctime, description) VALUES(?,?,?,?)",
                    (f.name, f.path, str(f.ctime), f.description))
                f.id = cur.lastrowid
            files.append(f)

        files.extend(self.files)
        self.showFiles(files)

        e.ignore()

    def contextMenuEvent(self, e: QtGui.QContextMenuEvent) -> None:
        item = self.itemAt(e.pos())
        if not item:
            e.ignore()
            return
        menu = QtWidgets.QMenu(self)
        open = QtGui.QAction('open', self)
        open.triggered.connect(partial(self.open_file, item))
        edit = QtGui.QAction('edit', self)
        edit.triggered.connect(partial(self.edit_file, item))
        path = QtGui.QAction('path', self)
        path.triggered.connect(partial(self.file_path, item))
        menu.addActions([open, edit, path])
        menu.popup(e.globalPos())

    def get_file_by_index(self, ind):
        return self.files[ind]

    def get_path_by_index(self, ind):
        return self.setting.get_absolute_path(self.get_file_by_index(ind).path)

    def open_file(self, item: QtWidgets.QTableWidgetItem):
        os.startfile(self.get_path_by_index(item.row()))

    def edit_file(self, item: QtWidgets.QTableWidgetItem):
        win = FileWin(self.setting, self.get_file_by_index(item.row()))
        win.show()
        self.wins.append(win)

    def file_path(self, item: QtWidgets.QTableWidgetItem):
        subprocess.Popen(
            f'explorer /select,"{self.get_path_by_index(item.row())}"')

    def del_file(self):
        rows = sorted({item.row() for item in self.selectedItems()})
        ids = []
        names = []
        conn = self.setting.conn
        for row in rows:
            f = self.files[row]
            ids.append(f.id)
            names.append(f.name)
        match QtWidgets.QMessageBox.question(self, "是否删除以下文件？", "\n".join(names), QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Ok):
            case QtWidgets.QMessageBox.Ok:
                with conn:
                    conn.execute("DELETE FROM files WHERE id in (?)",
                                 (",".join(str(id) for id in ids)))
                    conn.execute("DELETE FROM file_labels WHERE file_id in (?)",
                                 (",".join(str(id) for id in ids)))
                    for i in reversed(rows):
                        f = self.files.pop(i)
                        p = pathlib.Path(f.path)
                        if not p.is_absolute():
                            p = self.setting.root_path.joinpath(p)
                            p.unlink()
                    self.showFiles()
