import base64
import copy
import pathlib
import subprocess
from dataclasses import dataclass
from datetime import datetime
from functools import partial
from typing import List

from PySide6 import QtCore, QtGui, QtWidgets

from .fileUi import Ui_MainWindow
from .setting import Setting


@dataclass
class File:
    id: int
    name: str
    path: str
    is_dir: bool
    tags: List[str]
    ctime: datetime
    icon: str
    description: str


class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    reshow = QtCore.Signal(int)

    def __init__(self, setting: Setting, file: File) -> None:
        super().__init__()
        self.setupUi(self)

        self.setting = setting
        self.origin_file = file
        self.idLineEdit.setText(str(file.id))
        self.nameLineEdit.setText(file.name)
        self.dateTimeEdit.setDateTime(file.ctime)
        self.tagLineEdit.setText(
            " ".join(['#' + tag for tag in file.tags]))
        if file.icon:
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(base64.b64decode(file.icon))
            self.iconLabel.setPixmap(pixmap)
        else:
            p = QtWidgets.QFileIconProvider()
            if file.is_dir:
                icon = p.icon(p.IconType.Folder)
            else:
                icon = p.icon(QtCore.QFileInfo(pathlib.Path(file.path).name))
            self.iconLabel.setPixmap(icon.pixmap(10, 10))

        self.plainTextEdit.setPlainText(file.description)

        self.pathPushButton.clicked.connect(
            partial(subprocess.Popen, f'explorer /select,"{setting.get_absolute_path(file.path)}"'))
        self.cancelPushButton.clicked.connect(lambda: self.close())
        self.confirmPushButton.clicked.connect(self.confirm)
        self.iconFolderPushButton.clicked.connect(self.folder_choose)
        self.iconChoosePushButton.clicked.connect(self.icon_choose)
        self.iconImageChoosePushButton.clicked.connect(self.image_choose)

    def confirm(self):
        file = copy.deepcopy(self.origin_file)
        file.name = self.nameLineEdit.text()
        file.ctime = self.dateTimeEdit.dateTime().toPython()
        file.tags = [tag for part in self.tagLineEdit.text(
        ).split() if (tag := part.strip().strip('#'))]

        b = QtCore.QByteArray()
        buffer = QtCore.QBuffer(b)
        buffer.open(QtCore.QIODevice.WriteOnly)
        self.iconLabel.pixmap().save(buffer, 'PNG')
        buffer.close()
        file.icon = base64.b64encode(b.data())

        file.description = self.plainTextEdit.toPlainText()

        conn = self.setting.conn
        with conn:
            conn.execute(
                "UPDATE files SET name = ?, path = ?, ctime = ?, icon = ?, description = ? WHERE id = ?", (file.name, file.path, str(file.ctime), file.icon, file.description, file.id))
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

        self.reshow.emit(file.id)
        self.close()

    def folder_choose(self):
        self.iconLabel.setPixmap(QtWidgets.QFileIconProvider().icon(
            QtWidgets.QFileIconProvider.IconType.Folder).pixmap(20, 20, QtGui.QIcon.Mode.Normal))

    def icon_choose(self):
        f, typ = QtWidgets.QFileDialog.getOpenFileName(self, "choose an icon", str(
            pathlib.Path(self.setting.get_absolute_path(self.origin_file.path)).parent))
        if not f:
            return
        pixmap = QtWidgets.QFileIconProvider().icon(
            QtCore.QFileInfo(f)).pixmap(10, 10, QtGui.QIcon.Mode.Normal)
        self.iconLabel.setPixmap(pixmap)

    def image_choose(self):
        f, typ = QtWidgets.QFileDialog.getOpenFileName(self, "choose an image", str(
            pathlib.Path(self.setting.get_absolute_path(self.origin_file.path)).parent))
        if not f:
            return
        pixmap = QtGui.QPixmap()
        pixmap.load(f)
        if pixmap.width() > pixmap.height():
            pixmap = pixmap.scaledToWidth(20)
        else:
            pixmap = pixmap.scaledToHeight(20)
        self.iconLabel.setPixmap(pixmap)
