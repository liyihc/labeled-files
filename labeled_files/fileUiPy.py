import copy
from dataclasses import dataclass
from datetime import datetime
import sqlite3
from typing import List
from PySide6 import QtWidgets, QtCore, QtGui
from .fileUi import Ui_MainWindow


@dataclass
class File:
    id: int
    name: str
    path: str
    tags: List[str]
    ctime: datetime
    mtime: datetime
    description: str


class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    confirmed = QtCore.Signal(File)

    def __init__(self, setting, file: File) -> None:
        super().__init__()
        self.setupUi(self)

        self.setting = setting
        self.origin_file = file
        self.idLineEdit.setText(str(file.id))
        self.nameLineEdit.setText(file.name)
        self.dateTimeEdit.setDateTime(file.ctime)
        self.pathPushButton.clicked.connect(
            lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(file.path)))

        self.tagPlainTextEdit.setPlainText(
            " ".join(['#' + tag for tag in file.tags]))

        self.plainTextEdit.setPlainText(file.description)
        self.cancelPushButton.clicked.connect(lambda: self.close())
        self.confirmPushButton.clicked.connect(self.confirm)

    def confirm(self):
        file = copy.deepcopy(self.origin_file)
        file.name = self.nameLineEdit.text()
        file.ctime = self.dateTimeEdit.dateTime().toPython()
        file.tags = [tag for part in self.tagPlainTextEdit.toPlainText(
        ).split() if (tag := part.strip().strip('#'))]
        file.description = self.plainTextEdit.toPlainText()
        self.confirmed.emit(file)
        self.close()
