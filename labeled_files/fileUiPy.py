import copy
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
    tags: List[str]
    ctime: datetime
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
        self.pathPushButton.clicked.connect(
            partial(subprocess.Popen, f'explorer /select,"{setting.get_absolute_path(file.path)}"'))
        self.tagLineEdit.setText(
            " ".join(['#' + tag for tag in file.tags]))

        self.plainTextEdit.setPlainText(file.description)
        self.cancelPushButton.clicked.connect(lambda: self.close())
        self.confirmPushButton.clicked.connect(self.confirm)

    def confirm(self):
        file = copy.deepcopy(self.origin_file)
        file.name = self.nameLineEdit.text()
        file.ctime = self.dateTimeEdit.dateTime().toPython()
        file.tags = [tag for part in self.tagLineEdit.text(
        ).split() if (tag := part.strip().strip('#'))]
        file.description = self.plainTextEdit.toPlainText()

        conn = self.setting.conn
        with conn:
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

        self.setting.update_completer()
        self.reshow.emit(file.id)
        self.close()
