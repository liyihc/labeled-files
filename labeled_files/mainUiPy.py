from __future__ import annotations
from ast import keyword
from copy import copy
import dataclasses
import json

import pathlib
import sys
from collections import Counter
from functools import partial
from typing import List, Tuple

from PySide6 import QtCore, QtGui, QtWidgets

from .mainUi import Ui_MainWindow
from .path_types import init_handlers, path_handler_types
from .setting import VERSION, Config, setting, logv
from .sql import File
from .tree import build_tree
from .utils import get_shown_timedelta
from .flow_layout import FlowLayout


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

        self.table = FileTable(self)
        self.fileVerticalLayout.addWidget(self.table)

        self.tagListWidget.itemClicked.connect(self.remove_tag)
        self.tagListWidget.contextMenuEvent = self.tagListRightClicked

        self.pinTagLayout = FlowLayout()
        self.pinTagWidget.setLayout(self.pinTagLayout)
        self.treeWidget.itemDoubleClicked.connect(
            self.filter_with_tag_tree_item)
        self.treeWidget.contextMenuEvent = self.tagContextMenuEvent

        self.tagLineEdit.textChanged.connect(self.show_tags)
        self.tagSearchClearPushButton.clicked.connect(
            lambda: self.tagLineEdit.clear())
        self.searchPushButton.clicked.connect(self.search)
        self.openWorkSpaceAction.triggered.connect(self.open_workspace)
        self.clearSearchPushButton.clicked.connect(self.clear_search)
        self.delPushButton.clicked.connect(self.table.del_file)

        self.tags: List[Tuple[str, int]] = []

    def init_config(self):
        config_path = pathlib.Path("config.json")
        if config_path.exists():
            setting.config = Config.from_json(config_path.read_text())
        else:
            setting.config = Config()
        with config_path.open('w') as out:
            json.dump(dataclasses.asdict(setting.config), out, indent=4)

        self.menu.addSeparator()
        for space, path in setting.config.workspaces.items():
            self.menu.addAction(space).triggered.connect(
                partial(self.change_workspace, path))

        default = setting.config.workspaces.get(setting.config.default, None)
        init_handlers()
        for name, handler in path_handler_types.items():
            if handler.create_file_able(name):
                self.addFileMenu.addAction(name).triggered.connect(
                    partial(self.add_file, name))

        if default:
            self.change_workspace(default)

    def open_workspace(self):
        ret = QtWidgets.QFileDialog.getExistingDirectory(
            caption="open a folder as workspace")
        if ret:
            self.change_workspace(ret)

    def change_workspace(self, path):
        setting.set_root(path)
        self.last_keyword = None
        self.refresh_pin_tag()
        self.search()

    def search(self):
        if not setting.root_path:
            return
        keyword = self.searchLineEdit.text().strip()

        tags = [self.tagListWidget.item(row).text()
                for row in range(self.tagListWidget.count())]

        logv("SEARCH", f"keyword='{keyword}' tag='{str(tags)}'")

        conn = setting.conn
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
        setting.searched_tags = tags
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
        self.tags = tags

        self.show_tags()

    def show_tags(self):
        keyword = self.tagLineEdit.text().lower()
        if keyword:
            tags = [(tag, count)
                    for tag, count in self.tags if keyword in tag.lower()]
        else:
            tags = self.tags
        build_tree(self.treeWidget, tags)

    def show_all_tags(self):
        conn = setting.conn
        sql = f"SELECT label, COUNT(*) FROM file_labels GROUP BY label ORDER BY label"
        self.tags = conn.execute(sql).fetchall()
        self.show_tags()

    def filter_with_tag_tree_item(self, item: QtWidgets.QTreeWidgetItem):
        tag = self.get_tag_from_item(item)
        self.filter_with_tag(tag)

    def filter_with_tag(self, tag: str, insert_row: int = -1):
        for row in range(self.tagListWidget.count()):
            it = self.tagListWidget.item(row)
            text: str = it.text()
            if text.startswith(tag):
                return
            elif tag.startswith(text):
                it.setText(tag)
                self.search()
                return
        item = QtWidgets.QListWidgetItem(
            self.style().standardIcon(QtWidgets.QStyle.SP_TitleBarCloseButton), tag)
        if insert_row < 0:
            self.tagListWidget.addItem(item)
        else:
            self.tagListWidget.insertItem(insert_row, item)
        self.search()

    def refresh_pin_tag(self):
        layout = self.pinTagLayout
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()

        pin_tags = setting.conn.get_pin_tags()
        for tag in pin_tags:
            btn = QtWidgets.QToolButton()
            btn.setToolButtonStyle(
                QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            btn.setIcon(self.style().standardIcon(
                QtWidgets.QStyle.SP_FileDialogContentsView))
            btn.setText(tag.tag)
            layout.addWidget(btn)
            btn.clicked.connect(partial(self.filter_with_tag, tag.tag))

    def get_tag_from_item(self, item: QtWidgets.QTreeWidgetItem):
        tag = []
        while item:
            tag.append(item.text(0))
            item = item.parent()
        return '/'.join(reversed(tag))

    def pin_tag(self, tag: str):
        setting.conn.append_pin_tag(tag)
        self.refresh_pin_tag()

    def unpin_tag(self, tag: str):
        setting.conn.remove_pin_tag(tag)
        self.refresh_pin_tag()

    def tagContextMenuEvent(self, e: QtGui.QContextMenuEvent) -> None:
        root_self = self
        self = self.treeWidget
        item = self.itemAt(e.pos())
        if not item:
            e.ignore()
            return
        menu = QtWidgets.QMenu(self)

        tag = root_self.get_tag_from_item(item)
        menu.addAction('以标签筛选').triggered.connect(
            partial(root_self.filter_with_tag, tag))
        if not setting.conn.exist_pin_tag(tag):
            menu.addAction('钉住').triggered.connect(
                partial(root_self.pin_tag, tag))
        else:
            menu.addAction('取消钉住').triggered.connect(
                partial(root_self.unpin_tag, tag))
        menu.popup(e.globalPos())

    def remove_tag(self, item: QtWidgets.QListWidgetItem):
        self.tagListWidget.takeItem(
            self.tagListWidget.indexFromItem(item).row())
        self.search()

    def tagListRightClicked(self, e: QtGui.QContextMenuEvent):
        item = self.tagListWidget.itemAt(e.pos())
        if not item:
            e.ignore()
            return
        tag = item.text()
        find = tag.rfind('/')
        if find > 0:
            tag = tag[:find]
        else:
            tag = ""
        row = self.tagListWidget.indexFromItem(item).row()
        self.tagListWidget.takeItem(row)
        if tag:
            self.filter_with_tag(tag, row)
        else:
            self.search()

    def clear_search(self):
        self.searchLineEdit.clear()
        self.tagListWidget.clear()
        self.search()

    def add_file(self, handler_name: str):
        file = path_handler_types[handler_name].create_file(handler_name)
        setting.conn.insert_file(file)
        self.table.files.insert(0, file)
        self.table.showFiles()

    def __del__(self):
        conn = setting.conn
        if conn:
            conn.commit()
            conn.close()


class FileTable(QtWidgets.QTableWidget):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setAcceptDrops(True)
        self.setSortingEnabled(False)
        self.verticalHeader().setHidden(True)
        self.horizontalHeader().setStretchLastSection(True)

        self.setHorizontalScrollMode(
            QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["标签", "种类", "文件名", "上次访问时间", "描述"])
        h = self.horizontalHeader()
        for i, size in enumerate([150, 50, 125, 100]):
            h.resizeSection(i, size)

        self.files: List[File] = []
        self.itemDoubleClicked.connect(self.open_file)
        self.wins = []

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
        if setting.config.hide_search_tag_in_result:
            tags = []
            for tag in f.tags:
                for st in setting.searched_tags:
                    if tag == st:
                        break
                    tmp = st + '/'
                    if tag.startswith(tmp):
                        result = tag.removeprefix(tmp)
                        tags.append(result)
                        break
                else:
                    tags.append(tag)
        else:
            tags = f.tags
        item = QtWidgets.QTableWidgetItem(
            icon, ' '.join('#' + tag for tag in tags))
        self.setItem(row, 0, item)
        cols = [
            f.type,  # f.handler.get_shown_name()
            f.name,
            get_shown_timedelta(f.vtime) + "前",
            f.description
        ]
        for i, col in enumerate(cols, 1):
            self.setItem(row, i, QtWidgets.QTableWidgetItem(col))

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
        conn = setting.conn
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
        menu.addAction("打开").triggered.connect(partial(self.open_file, item))
        menu.addAction('编辑').triggered.connect(partial(self.edit_file, item))
        menu.addAction("创建副本").triggered.connect(
            partial(self.duplicate_file, item))
        menu.addAction('打开文件夹').triggered.connect(
            partial(self.file_path, item))
        menu.popup(e.globalPos())

    def get_file_by_index(self, ind: int, visit: bool = True) -> File:
        f = self.files[ind]
        if visit:
            setting.conn.visit(f.id)
        return f

    def duplicate_file(self, item: QtWidgets.QTableWidgetItem):
        f = copy(self.get_file_by_index(item.row(), False))
        setting.conn.insert_file(f)
        self.files.insert(0, f)
        self.insertRow(0)
        self.showat(0, f)

    def open_file(self, item: QtWidgets.QTableWidgetItem):
        self.get_file_by_index(item.row()).handler.open()

    def edit_file(self, item: QtWidgets.QTableWidgetItem):
        f = self.get_file_by_index(item.row())
        f.handler.edit(partial(self.reshowat, f.id, item.row()))

    def reshowat(self, file_id, row: int):
        conn = setting.conn
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
        conn = setting.conn
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
