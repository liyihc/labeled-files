from __future__ import annotations

import pathlib
import sys
from collections import Counter
from functools import partial
from typing import List

from PySide6 import QtCore, QtGui, QtWidgets

from .mainUi import Ui_MainWindow
from .path_types import init_handlers, path_handler_types
from .setting import VERSION, Config, Setting, logv
from .sql import File
from .tree import build_tree


def except_hook(exc_type, exc_value, exc_traceback):
    import logging
    exception = logging.getLogger("exception")
    exception.exception(exc_value, exc_info=exc_value)
    QtWidgets.QMessageBox.information(None, "错误", str(exc_value))


sys.excepthook = except_hook


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
            self.menu.addAction(space).triggered.connect(
                partial(self.change_workspace, path))

        self.table = FileTable(self.setting, self)
        self.fileVerticalLayout.addWidget(self.table)

        self.tagListWidget.itemClicked.connect(self.remove_tag)
        self.treeWidget.itemDoubleClicked.connect(self.doubleclick_tag)
        self.searchPushButton.clicked.connect(self.search)
        self.openWorkSpaceAction.triggered.connect(self.open_workspace)
        self.clearTagPushButton.clicked.connect(self.clear_tag)
        self.delPushButton.clicked.connect(self.table.del_file)

        default = self.config.workspaces.get(self.config.default, None)
        if default:
            self.setting.set_root(default)
        init_handlers(self.setting)
        for name, handler in path_handler_types.items():
            if handler.create_file_able(name):
                self.addFileMenu.addAction(name).triggered.connect(
                    partial(self.add_file, name))

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

        tags = [self.tagListWidget.item(row).text()
                for row in range(self.tagListWidget.count())]

        logv("SEARCH", f"keyword='{keyword}' tag='{str(tags)}'")

        conn = self.setting.conn
        match keyword, tags:
            case "", []:
                file_ids = [f for f, in conn.execute(
                    "SELECT id FROM files ORDER BY vtime DESC LIMIT 50")]
            case keyword, []:
                file_ids = [f for f, in conn.execute(
                    f'SELECT id FROM files WHERE name like "%{keyword}%" ORDER BY vtime DESC')]
            case keyword, tags:
                tag = tags[0]
                file_ids = {v for v, in conn.execute(
                    f"SELECT file_id FROM file_labels WHERE label = '{tag}' OR label LIKE '{tag}/%'")}
                for tag in tags[1:]:
                    if file_ids:
                        file_ids = ','.join(map(str, file_ids))
                        file_ids = {v for v, in conn.execute(
                            f"SELECT file_id FROM file_labels WHERE file_id in ({file_ids}) AND (label = '{tag}' OR label LIKE '{tag}/%')")}

                if file_ids and keyword:
                    file_ids = ','.join(str(f) for f in file_ids)
                    file_ids = [f for f, in conn.execute(
                        f'SELECT id FROM files WHERE name like "%{keyword}%" AND id in ({file_ids}) ORDER BY vtime DESC')]
        if file_ids:
            file_ids = ','.join(str(f) for f in file_ids)
            files = conn.fetch_files(
                f"SELECT * FROM files WHERE id in ({file_ids}) ORDER BY vtime DESC")
        else:
            files = []
        self.table.showFiles(files)

        if not keyword and not tags:
            self.show_all_tags()
        else:
            self.show_file_tags(files)

    def show_file_tags(self, files: List[File]):
        # SELECT label, COUNT(*) FROM file_labels WHERE file_id in file_id_list GROUP BY label ORDER BY label
        counter = Counter()
        for f in files:
            counter.update(f.tags)
        tags = list(counter.items())
        tags.sort(key=lambda v: v[0])

        build_tree(self.treeWidget, tags)

    def show_all_tags(self):
        conn = self.setting.conn
        sql = f"SELECT label, COUNT(*) FROM file_labels GROUP BY label ORDER BY label"
        tags = conn.execute(sql).fetchall()

        build_tree(self.treeWidget, tags)

    def doubleclick_tag(self, item: QtWidgets.QTreeWidgetItem):
        tag = []
        while item:
            tag.append(item.text(0))
            item = item.parent()
        tag = '/'.join(reversed(tag))
        for row in range(self.tagListWidget.count()):
            it = self.tagListWidget.item(row)
            text: str = it.text()
            if text.startswith(tag):
                return
            elif tag.startswith(text):
                it.setText(tag)
                return

        self.tagListWidget.addItem(QtWidgets.QListWidgetItem(
            self.style().standardIcon(QtWidgets.QStyle.SP_TitleBarCloseButton), tag))
        self.search()

    def remove_tag(self, item: QtWidgets.QListWidgetItem):
        self.tagListWidget.takeItem(
            self.tagListWidget.indexFromItem(item).row())
        self.search()

    def clear_tag(self):
        self.tagListWidget.clear()
        self.search()

    def add_file(self, handler_name: str):
        file = path_handler_types[handler_name].create_file(handler_name)
        self.setting.conn.insert_file(file)
        self.table.files.insert(0, file)
        self.table.showFiles()

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
        for row, file in enumerate(results):
            self.showat(row, file)

    def showat(self, row: int, f: File):
        icon = f.handler.get_icon()
        item = QtWidgets.QTableWidgetItem(icon, f.name)
        self.setItem(row, 0, item)
        self.setItem(row, 1, QtWidgets.QTableWidgetItem(
            f.ctime.strftime("%y%m%d %H:%M:%S")))
        self.setItem(row, 2, QtWidgets.QTableWidgetItem(
            ' '.join('#' + tag for tag in f.tags)))
        self.setItem(row, 3, QtWidgets.QTableWidgetItem(f.description))

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        data = event.mimeData()
        text = data.text().splitlines()
        if text:
            for handler in path_handler_types.values():
                if handler.mime_acceptable(text[0]):
                    event.accept()

    def dragMoveEvent(self, e: QtGui.QDragMoveEvent) -> None:
        if e.pos().y() < self.height() / 2:
            if e.pos().x() < self.width() / 2:
                e.setDropAction(QtCore.Qt.DropAction.MoveAction)
            else:
                e.setDropAction(QtCore.Qt.DropAction.CopyAction)
        else:
            e.setDropAction(QtCore.Qt.DropAction.LinkAction)

    def dropEvent(self, e: QtGui.QDropEvent) -> None:
        self.dragMoveEvent(e)

        action = e.dropAction()
        conn = self.setting.conn
        files = []
        for file in e.mimeData().text().splitlines():
            for typ, handler in path_handler_types.items():
                if not handler.mime_acceptable(file):
                    continue
                f = handler.create_file_from_mime(file)
                match action:
                    case QtCore.Qt.DropAction.MoveAction:
                        f.handler.move_to()
                    case QtCore.Qt.DropAction.CopyAction:
                        f.handler.copy_to()
                conn.insert_file(f)
                files.append(f)
                break

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
        self.setting.conn.visit(f.id)
        return f

    def open_file(self, item: QtWidgets.QTableWidgetItem):
        self.get_file_by_index(item.row()).handler.open()

    def edit_file(self, item: QtWidgets.QTableWidgetItem):
        f = self.get_file_by_index(item.row())
        f.handler.edit(partial(self.reshowat, f.id, item.row()))

    def reshowat(self, file_id, row: int):
        conn = self.setting.conn
        f = conn.fetch_files(
            "SELECT * FROM files WHERE id = ? ", (file_id,))[0]
        self.files[row] = f
        self.showat(row, f)

    def file_path(self, item: QtWidgets.QTableWidgetItem):
        self.get_file_by_index(item.row()).handler.open_path()

    def del_file(self):
        rows = sorted({item.row() for item in self.selectedItems()})
        ids = []
        names = []
        conn = self.setting.conn
        for row in rows:
            f = self.files[row]
            ids.append(f.id)
            names.append(f.handler.repr())
        match QtWidgets.QMessageBox.question(self, "是否删除以下文件？", "\n".join(names), QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Ok):
            case QtWidgets.QMessageBox.Ok:
                try:
                    for i in reversed(rows):
                        f = self.files.pop(i)
                        f.handler.remove()
                        conn.delete_file([f.id])
                except:
                    raise
                finally:
                    self.showFiles()
