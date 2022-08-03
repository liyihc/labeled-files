from __future__ import annotations
from copy import copy
import dataclasses
from datetime import datetime
import json

import pathlib
import re
import sys
from collections import Counter, defaultdict
from functools import partial
from typing import Dict, List, Tuple

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


# TODO:
# - 支持多语言
# - 文件列表中，标签显示可视化，即名字+标签
# - 为减少冲突，将访问与真正的文件区分开，根据主机ID区分即可
# - 文件类型应当支持保存浏览器网页（加一个插件）

# FUTURE
# - 支持安装

class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(f"Labeled Files {VERSION}")

        h = self.filesTableWidget.horizontalHeader()
        for i, size in enumerate([150, 50, 125, 100]):
            h.resizeSection(i, size)

        self.tagListWidget.itemClicked.connect(self.search_tag_remove)
        self.tagListWidget.contextMenuEvent = self.search_tag_RightClicked

        self.pinTagLayout = FlowLayout()
        self.pinTagWidget.setLayout(self.pinTagLayout)
        self.treeWidget.itemDoubleClicked.connect(
            self.tag_tree_item_append)
        self.treeWidget.contextMenuEvent = self.tag_tree_ContextMenuEvent

        self.tagLineEdit.textChanged.connect(self.tag_tree_show)
        self.tagSearchClearPushButton.clicked.connect(
            lambda: self.tagLineEdit.clear())
        self.searchPushButton.clicked.connect(self.search)
        self.openWorkSpaceAction.triggered.connect(self.workspace_open)
        self.clearSearchPushButton.clicked.connect(self.search_clear_all)
        self.filesTableWidget.itemDoubleClicked.connect(
            self.file_table_file_open)

        self.filesTableWidget.dragEnterEvent = self.file_table_DragEnterEvent
        self.filesTableWidget.dragMoveEvent = self.file_table_DragMoveEvent
        self.filesTableWidget.dropEvent = self.file_table_DropEvent
        self.filesTableWidget.contextMenuEvent = self.file_table_ContextMenuEvent

        self.delPushButton.clicked.connect(self.file_table_file_del)

        self.files: List[File] = []
        self.tags: List[Tuple[str, int, datetime]] = []

    def config_init(self):
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
                partial(self.workspace_change, path))

        default = setting.config.workspaces.get(setting.config.default, None)
        init_handlers()
        for name, handler in path_handler_types.items():
            if handler.create_file_able(name):
                self.addFileMenu.addAction(name).triggered.connect(
                    partial(self.file_table_create_file, name))

        if default:
            self.workspace_change(default)

    def workspace_open(self):
        ret = QtWidgets.QFileDialog.getExistingDirectory(
            caption="open a folder as workspace")
        if ret:
            self.workspace_change(ret)

    def workspace_change(self, path):
        setting.set_root(path)
        self.last_keyword = None
        self.pin_tag_refresh()
        self.search()

    def search(self):
        if not setting.root_path:
            return
        keyword = self.searchLineEdit.text().strip()

        tags = self.search_tag_get()

        logv("SEARCH", f"keyword='{keyword}' tag='{str(tags)}'")

        conn = setting.conn
        with conn.connect():
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
            self.file_table_show_files(files)

            if not keyword and not tags:
                self.tag_tree_show_all()
            else:
                self.tag_tree_show_files(files)

    def search_tag_get(self):
        return [self.tagListWidget.item(row).text()
                for row in range(self.tagListWidget.count())]

    def tag_tree_show_files(self, files: List[File]):
        default_value = (0, datetime(1970, 1, 1))
        counter: Dict[str, (int, datetime)] = defaultdict(
            lambda: default_value)
        for f in files:
            for tag in tags:
                cnt, dt = counter[tag]
                counter[tag] = (cnt + 1, max(f.vtime, dt))
        tags = [(k, v1, v2) for k, (v1, v2) in counter]
        tags.sort(key=lambda v: (v[2], v[1]), reverse=True)
        self.tags = tags

        self.tag_tree_show()

    def tag_tree_show(self):
        keyword = self.tagLineEdit.text().lower()
        if keyword:
            tags = [(tag, count, vtime)
                    for tag, count, vtime in self.tags if keyword in tag.lower()]
        else:
            tags = self.tags
        build_tree(self.treeWidget, tags)

    def tag_tree_show_all(self):
        conn = setting.conn
        sql = f"""
            SELECT fl.label, COUNT(*) c, MAX(fs.vtime) t
            FROM file_labels fl
            LEFT JOIN files fs
            ON fl.file_id == fs.id
            GROUP BY fl.label 
            ORDER BY t DESC, c DESC"""
        with conn.connect():
            self.tags = [(tag, cnt, datetime.fromisoformat(vtime))
                         for tag, cnt, vtime in conn.execute(sql).fetchall()]
        self.tag_tree_show()

    def tag_tree_item_append(self, item: QtWidgets.QTreeWidgetItem):
        tag = self.tag_tree_get_from_item(item)
        self.search_tag_insert(tag)

    def search_tag_insert(self, tag: str, insert_row: int = -1):
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

    def pin_tag_refresh(self):
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
            btn.clicked.connect(partial(self.search_tag_insert, tag.tag))

    def tag_tree_get_from_item(self, item: QtWidgets.QTreeWidgetItem):
        tag = []
        while item:
            tag.append(item.text(0))
            item = item.parent()
        return '/'.join(reversed(tag))

    def pin_tag_pin(self, tag: str):
        setting.conn.append_pin_tag(tag)
        self.pin_tag_refresh()

    def pin_tag_unpin(self, tag: str):
        setting.conn.remove_pin_tag(tag)
        self.pin_tag_refresh()

    def tag_tree_ContextMenuEvent(self, e: QtGui.QContextMenuEvent) -> None:
        root_self = self
        self = self.treeWidget
        item = self.itemAt(e.pos())
        if not item:
            e.ignore()
            return
        menu = QtWidgets.QMenu(self)

        tag = root_self.tag_tree_get_from_item(item)
        menu.addAction('以标签筛选').triggered.connect(
            partial(root_self.search_tag_insert, tag))
        if not setting.conn.exist_pin_tag(tag):
            menu.addAction('钉住').triggered.connect(
                partial(root_self.pin_tag_pin, tag))
        else:
            menu.addAction('取消钉住').triggered.connect(
                partial(root_self.pin_tag_unpin, tag))
        menu.popup(e.globalPos())

    def search_tag_remove(self, item: QtWidgets.QListWidgetItem):
        self.tagListWidget.takeItem(
            self.tagListWidget.indexFromItem(item).row())
        self.search()

    def search_tag_RightClicked(self, e: QtGui.QContextMenuEvent):
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
            self.search_tag_insert(tag, row)
        else:
            self.search()

    def search_clear_all(self):
        self.searchLineEdit.clear()
        self.tagListWidget.clear()
        self.search()

    def file_table_create_file(self, handler_name: str):
        file = path_handler_types[handler_name].create_file(handler_name)
        file.tags = self.search_tag_get()
        setting.conn.insert_file(file)
        self.files.insert(0, file)
        self.file_table_show_files()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        setting.conn.close_db()
        return super().closeEvent(event)

    def file_table_show_files(self, results: List[File] = None):
        table = self.filesTableWidget
        table.clearContents()
        table.setRowCount(0)
        if results is not None:
            self.files = results
        else:
            results = self.files
        table.setRowCount(len(results))
        for row, file in enumerate(results):
            self.file_table_show_file_at(row, file)

    def file_table_show_file_at(self, row: int, f: File):
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
        table = self.filesTableWidget
        table.setItem(row, 0, item)
        if setting.config.file_name_regex and f.name.startswith("r|"):
            actual_name = f.handler.actual_name_get()
            ret = re.search(f.name.removeprefix('r|'), actual_name)
            if ret:
                name = ret.group()
            else:
                name = f"MISS FINDING {f.name} in {actual_name}"
        else:
            name = f.name
        cols = [
            f.type,  # f.handler.get_shown_name()
            name,
            get_shown_timedelta(f.vtime) + "前",
            f.description
        ]
        for i, col in enumerate(cols, 1):
            table.setItem(row, i, QtWidgets.QTableWidgetItem(col))

    def file_table_DragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        data = event.mimeData()
        text = data.text().splitlines()
        if text:
            for handler in path_handler_types.values():
                if handler.mime_acceptable(text[0]):
                    event.accept()

    def file_table_DragMoveEvent(self, e: QtGui.QDragMoveEvent) -> None:
        table = self.filesTableWidget
        if e.pos().y() < table.height() / 2:
            if e.pos().x() < table.width() / 2:
                e.setDropAction(QtCore.Qt.DropAction.MoveAction)
            else:
                e.setDropAction(QtCore.Qt.DropAction.CopyAction)
        else:
            e.setDropAction(QtCore.Qt.DropAction.LinkAction)

    def file_table_DropEvent(self, e: QtGui.QDropEvent) -> None:
        self.file_table_DragMoveEvent(e)

        action = e.dropAction()
        conn = setting.conn
        files = []
        current_tags = self.search_tag_get()
        with conn.connect():
            for file in e.mimeData().text().splitlines():
                for typ, handler in path_handler_types.items():
                    if not handler.mime_acceptable(file):
                        continue
                    f = handler.create_file_from_mime(file)
                    f.tags = current_tags.copy()

                    match action:
                        case QtCore.Qt.DropAction.MoveAction:
                            f.handler.move_to()
                        case QtCore.Qt.DropAction.CopyAction:
                            f.handler.copy_to()
                    conn.insert_file(f)
                    files.append(f)
                    break

        files.extend(self.files)
        self.file_table_show_files(files)

        e.ignore()

    def file_table_ContextMenuEvent(self, e: QtGui.QContextMenuEvent) -> None:
        table = self.filesTableWidget
        item = table.itemAt(e.pos())
        if not item:
            e.ignore()
            return
        menu = QtWidgets.QMenu(table)
        menu.addAction("打开").triggered.connect(
            partial(self.file_table_file_open, item))
        menu.addAction('编辑').triggered.connect(
            partial(self.file_table_file_edit, item))
        menu.addAction("以标签筛选").triggered.connect(
            partial(self.file_table_file_filter, item))
        menu.addAction("创建副本").triggered.connect(
            partial(self.file_table_file_duplicate, item))
        menu.addAction('打开文件夹').triggered.connect(
            partial(self.file_table_file_path_open, item))
        menu.popup(e.globalPos())

    def file_table_get_file_by_index(self, ind: int, visit: bool = True) -> File:
        f = self.files[ind]
        if visit:
            setting.conn.visit(f.id)
        return f

    def file_table_file_filter(self, item: QtWidgets.QTableWidgetItem):
        f = self.file_table_get_file_by_index(item.row(), False)
        for tag in f.tags:
            self.search_tag_insert(tag)

    def file_table_file_duplicate(self, item: QtWidgets.QTableWidgetItem):
        origin_f = self.file_table_get_file_by_index(item.row(), False)
        custom = False
        if origin_f.handler.support_custom_duplicate:
            msg = QtWidgets.QMessageBox()
            msg.setText("如何创建副本？")
            msg.addButton(msg.StandardButton.Cancel)
            ref_btn = msg.addButton("创建引用副本", msg.ButtonRole.YesRole)
            cus_btn = msg.addButton("创建自定义副本", msg.ButtonRole.NoRole)
            msg.setDefaultButton(cus_btn)
            if msg.exec() == msg.StandardButton.Cancel:
                return
            click_btn = msg.clickedButton()
            if click_btn == cus_btn:
                custom = True
        if custom:
            f = origin_f.handler.custom_deplicate()
        else:
            f = copy(origin_f)
        if f is None:
            return
        setting.conn.insert_file(f)
        self.files.insert(0, f)
        self.filesTableWidget.insertRow(0)
        self.file_table_show_file_at(0, f)

    def file_table_file_open(self, item: QtWidgets.QTableWidgetItem):
        self.file_table_get_file_by_index(item.row()).handler.open()

    def file_table_file_edit(self, item: QtWidgets.QTableWidgetItem):
        f = self.file_table_get_file_by_index(item.row())
        f.handler.edit(
            partial(self.file_table_show_file_from_db, f.id, item.row()))

    def file_table_show_file_from_db(self, file_id, row: int):
        conn = setting.conn
        f = conn.fetch_files(
            "SELECT * FROM files WHERE id = ? ", (file_id,))[0]
        self.files[row] = f
        self.file_table_show_file_at(row, f)

    def file_table_file_path_open(self, item: QtWidgets.QTableWidgetItem):
        self.file_table_get_file_by_index(item.row()).handler.open_path()

    def file_table_file_del(self):
        rows = sorted({item.row()
                      for item in self.filesTableWidget.selectedItems()})
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
                    with conn.connect():
                        for i in reversed(rows):
                            f = self.files[i]
                            f.handler.remove()
                            conn.delete_file([f.id])
                            self.files.pop(i)
                except:
                    raise
                finally:
                    self.file_table_show_files()
