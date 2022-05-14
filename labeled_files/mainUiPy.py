from __future__ import annotations
import base64

import os
import pathlib
import random
import shutil
import sqlite3
import subprocess
from datetime import datetime
from functools import partial, reduce
from typing import List

from PySide6 import QtCore, QtGui, QtWidgets

from .fileUiPy import File
from .fileUiPy import Window as FileWin
from .mainUi import Ui_MainWindow
from .setting import Config, Setting, VERSION, logv
from .tree import build_tree
import sys


def except_hook(exc_type, exc_value, exc_traceback):
    import logging
    exception = logging.getLogger("exception")
    exception.exception(exc_value, exc_info=exc_value)
    QtWidgets.QMessageBox.information(None, "错误", str(exc_value))


sys.excepthook = except_hook

need_icon_suffixes = {".exe", "", ".lnk"}


class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(f"Labeled Files {VERSION}")
        self.setting = Setting()

        config_path = pathlib.Path("config.json")
        if config_path.exists():
            self.config = Config.parse_file(config_path)
        else:
            self.config = Config()

        self.menu.addSeparator()
        for space, path in self.config.workspaces.items():
            action = QtGui.QAction(space, self)
            action.triggered.connect(partial(self.change_workspace, path))
            self.menu.addAction(action)

        # TODO self.tagTableWidget.mimeData = tag_mime_data
        self.tagLineEdit.keyPressEvent = self.check_complete
        self.setting.lineedits.append(self.tagLineEdit)
        self.table = FileTable(self.setting, self)
        self.fileVerticalLayout.addWidget(self.table)

        self.tagListWidget.itemClicked.connect(self.remove_tag)
        self.treeWidget.itemDoubleClicked.connect(self.doubleclick_tag)
        # TODO: add context menu to tagtablewidget to edit tags
        self.searchPushButton.clicked.connect(self.search)
        self.openWorkSpaceAction.triggered.connect(self.open_workspace)
        self.delPushButton.clicked.connect(self.table.del_file)

        default = self.config.workspaces.get(self.config.default, None)
        if default:
            self.setting.set_root(default)
        self.last_keyword = None

    def open_workspace(self):
        ret = QtWidgets.QFileDialog.getExistingDirectory(
            caption="open a folder as workspace")
        if ret:
            self.change_workspace(ret)

    def change_workspace(self, path):
        self.setting.set_root(path)
        self.last_keyword = None
        self.search()

    def search(self):
        if not self.setting.root_path:
            return
        keyword = self.searchLineEdit.text().strip()
        logv("SEARCH", f"keyword {keyword}")
        if self.tagLineEdit.text():
            self.complete()
        tags = []
        for i in range(self.tagListWidget.count()):
            tags.append(self.tagListWidget.item(i).text())

        if self.last_keyword != keyword:
            self.search_tag(keyword)
        self.search_file(keyword, tags)
        self.last_keyword = keyword

    def search_tag(self, keyword):
        conn = self.setting.conn
        labels = conn.execute(
            "SELECT label, COUNT(*) FROM file_labels GROUP BY label ORDER BY label").fetchall()
        if keyword:
            labels = [(label, cnt)
                      for label, cnt in labels if keyword in label]

        build_tree(self.treeWidget, labels)

    def search_file(self, keyword, tags):
        conn = self.setting.conn
        if len(tags):
            file_ids = reduce(lambda a, b: a & b, map(
                lambda tag: {v for v, in conn.execute(f"SELECT file_id FROM file_labels WHERE label = '{tag}' OR label LIKE '{tag}/%'")}, tags))
            if keyword:
                file_ids = ','.join(str(f) for f in file_ids)
                file_ids = [f for f, in conn.execute(
                    f'SELECT id FROM files WHERE name like "%{keyword}%" AND id in ({file_ids}) ORDER BY ctime DESC')]
        elif keyword:
            file_ids = [f for f, in conn.execute(
                f'SELECT id FROM files WHERE name like "%{keyword}%" ORDER BY ctime DESC')]
        else:
            file_ids = [f for f, in conn.execute(
                "SELECT id FROM files ORDER BY vtime DESC LIMIT 50")]
        file_ids = ','.join(str(f) for f in file_ids)

        files: List[File] = [get_file(conn, record) for record in conn.execute(
            f"SELECT id, name, path, is_dir, ctime, vtime, icon, description FROM files WHERE id in ({file_ids}) ORDER BY vtime DESC")]

        self.table.showFiles(files)

    def check_complete(self, e: QtGui.QKeyEvent):
        match e.key():
            case 32:
                return self.complete()

        QtWidgets.QLineEdit.keyPressEvent(self.tagLineEdit, e)

    def complete(self):
        logv("COMPLETE")
        completer = self.tagLineEdit.completer()
        if completer.currentRow() >= 0:
            tag = completer.currentCompletion()
            self.tagLineEdit.setText("")
            self.add_tag(tag)

    def add_tag(self, tag: str):
        tags = [self.tagListWidget.item(i).text()
                for i in range(self.tagListWidget.count())]

        logv("TAG", f"add '{tag}' to '{','.join(tags)}'")
        if tag not in tags:
            self.tagListWidget.addItem(QtWidgets.QListWidgetItem(self.style().standardIcon(
                QtWidgets.QStyle.SP_TitleBarCloseButton), tag))
            self.search()

    def remove_tag(self, item: QtWidgets.QListWidgetItem):
        ind = self.tagListWidget.indexFromItem(item)
        self.tagListWidget.takeItem(ind.row())
        self.search()

    def doubleclick_tag(self, item: QtWidgets.QTreeWidgetItem):
        tag = []
        while item:
            tag.append(item.text(0))
            item = item.parent()
        while self.tagListWidget.count():
            self.tagListWidget.takeItem(0)
        self.add_tag('/'.join(reversed(tag)))

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
            self.showFileAt(row, file, icon_provider)

    def showFileAt(self, row, f: File, icon_provider: QtWidgets.QFileIconProvider = None):
        if f.icon:
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(base64.b64decode(f.icon))
            icon = QtGui.QIcon(pixmap)
        else:
            if not icon_provider:
                icon_provider = QtWidgets.QFileIconProvider()
            if f.is_dir:
                icon = icon_provider.icon(icon_provider.IconType.Folder)
            else:
                p = QtCore.QFileInfo(pathlib.Path(f.path).name)
                icon = icon_provider.icon(p)
        item = QtWidgets.QTableWidgetItem(icon, f.name)
        self.setItem(row, 0, item)
        self.setItem(row, 1, QtWidgets.QTableWidgetItem(
            f.ctime.strftime("%y%m%d %H:%M:%S")))
        self.setItem(row, 2, QtWidgets.QTableWidgetItem(
            ' '.join('#' + tag for tag in f.tags)))
        self.setItem(row, 3, QtWidgets.QTableWidgetItem(f.description))

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
        icon_privider = QtWidgets.QFileIconProvider()
        for file in e.mimeData().text().splitlines():
            p = pathlib.Path(file.removeprefix("file:///"))
            stat = p.stat()
            f = File(None, p.name, None, p.is_dir(), [], datetime.fromtimestamp(
                stat.st_ctime), "", "")
            p = func(p)
            f.path = str(p)
            if not f.is_dir and p.suffix.lower() in need_icon_suffixes:
                icon = icon_privider.icon(QtCore.QFileInfo(p))
                b = QtCore.QByteArray()
                buffer = QtCore.QBuffer(b)
                buffer.open(QtCore.QIODevice.WriteOnly)
                icon.pixmap(10, 10, QtGui.QIcon.Mode.Normal).save(
                    buffer, 'PNG')
                buffer.close()
                f.icon = base64.b64encode(b.data())
            with conn:
                cur = conn.execute(
                    f"INSERT INTO files(name, path, is_dir, ctime, vtime, icon, description) VALUES(?,?,?,?,?,?,?)",
                    (f.name, f.path, f.is_dir, str(f.ctime), str(datetime.now()), f.icon, f.description))
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
        f = self.files[ind]
        self.visit(f.id)
        return f

    def get_path_by_index(self, ind):
        return self.setting.get_absolute_path(self.get_file_by_index(ind).path)

    def visit(self, file_id):
        with self.setting.conn:
            self.setting.conn.execute(
                "UPDATE files SET vtime = ? WHERE id = ?", (str(datetime.now()), file_id))

    def open_file(self, item: QtWidgets.QTableWidgetItem):
        p = self.get_path_by_index(item.row())
        if p.exists():
            cwd = os.getcwd()
            os.chdir(p.parent)
            os.startfile(p)
            os.chdir(cwd)
        else:
            QtWidgets.QMessageBox.information(self, "文件不存在", str(p))

    def edit_file(self, item: QtWidgets.QTableWidgetItem):
        win = FileWin(self.setting, self.get_file_by_index(item.row()))
        win.show()
        win.reshow.connect(self.reshow)
        self.wins.append(win)

    def reshow(self, file_id):
        conn = self.setting.conn
        f = get_file(conn, conn.execute(
            "SELECT id, name, path, is_dir, ctime, vtime, icon, description FROM files WHERE id = ? LIMIT 1", (file_id,)).fetchone())
        for ind, rep in enumerate(self.files):
            if rep.id == file_id:
                self.files[ind] = f
                self.showFileAt(ind, f)
                break

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
            p = pathlib.Path(f.path)
            if p.is_absolute():
                names.append(f"link-to: {f.name}")
            else:
                names.append(f"file: {f.name}")
        match QtWidgets.QMessageBox.question(self, "是否删除以下文件？", "\n".join(names), QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Ok):
            case QtWidgets.QMessageBox.Ok:
                with conn:
                    ids = ",".join(str(id) for id in ids)
                    conn.execute(f"DELETE FROM files WHERE id in ({ids})")
                    conn.execute(
                        f"DELETE FROM file_labels WHERE file_id in ({ids})")
                    for i in reversed(rows):
                        f = self.files.pop(i)
                        p = pathlib.Path(f.path)
                        if not p.is_absolute():
                            p = self.setting.root_path.joinpath(p)
                            if p.exists():
                                p.unlink()
                    self.showFiles()


def get_file(conn: sqlite3.Connection, args):
    id, name, path, is_dir, ctime, vtime, icon, description = args
    tags = [tag for tag, in conn.execute(
        "SELECT label FROM file_labels WHERE file_id = ?", (id,))]
    return File(id, name, str(path), is_dir, tags, datetime.fromisoformat(ctime), icon, description)


def tag_mime_data(items: List[QtWidgets.QTableWidgetItem]):
    for item in items:
        if not item.column():
            data = QtCore.QMimeData()
            data.setText(item.text())
            return data
