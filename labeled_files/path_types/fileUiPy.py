import abc
import base64
import copy
import pathlib
import subprocess
from functools import partial

from PySide6 import QtCore, QtGui, QtWidgets

from .fileUi import Ui_MainWindow
from .base import Setting, File


class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    reshow = QtCore.Signal()

    def __init__(self, setting: Setting, widget: 'BaseWidget', file: File) -> None:
        super().__init__()
        self.setupUi(self)

        self.setting = setting
        self.origin_file = file
        self.idLineEdit.setText(str(file.id))
        self.nameLineEdit.setText(file.name)
        self.dateTimeEdit.setDateTime(file.ctime)
        self.tagLineEdit.setText(
            " ".join(['#' + tag for tag in file.tags]))
        self.icon = file.icon
        pixmap = file.handler.get_pixmap()
        pixmap.setDevicePixelRatio(self.devicePixelRatio())
        self.iconLabel.setPixmap(pixmap)

        self.plainTextEdit.setPlainText(file.description)

        self.sub_widget = widget
        widget.setupUi(self.widget)
        self.cancelPushButton.clicked.connect(lambda: self.close())
        self.confirmPushButton.clicked.connect(self.confirm)
        self.iconDefaultPushButton.clicked.connect(self.clear_image)
        self.iconChoosePushButton.clicked.connect(self.icon_choose)
        self.iconImageChoosePushButton.clicked.connect(self.image_choose)
        self.setWindowTitle(f"{file.type}：{file.name} - {' '.join(file.tags)}")

    def confirm(self):
        self.sub_widget.confirm_path()
        file = copy.deepcopy(self.origin_file)
        file.name = self.nameLineEdit.text()
        file.ctime = self.dateTimeEdit.dateTime().toPython()
        file.tags = [tag for part in self.tagLineEdit.text(
        ).split() if (tag := part.strip().strip('#'))]
        file.icon = self.icon
        file.path = self.sub_widget.path or file.path

        file.description = self.plainTextEdit.toPlainText()

        self.setting.conn.update_file(file)

        self.reshow.emit()
        self.close()

    def clear_image(self):
        self.icon = ""
        pixmap = self.origin_file.handler.icon_to_pixmap(
            self.origin_file.handler.get_default_icon())
        pixmap.setDevicePixelRatio(self.devicePixelRatio())
        self.iconLabel.setPixmap(pixmap)

    def icon_choose(self):
        f, typ = QtWidgets.QFileDialog.getOpenFileName(self, "choose an icon", str(
            self.origin_file.handler.get_absolute_path().parent))
        if not f:
            return
        pixmap = QtWidgets.QFileIconProvider().icon(
            QtCore.QFileInfo(f)).pixmap(20, 20, QtGui.QIcon.Mode.Normal)
        pixmap.setDevicePixelRatio(self.devicePixelRatio())
        self.iconLabel.setPixmap(pixmap)
        self.icon = self.origin_file.handler.pixmap_to_b64(pixmap)

    def image_choose(self):
        f, typ = QtWidgets.QFileDialog.getOpenFileName(self, "choose an image", str(
            self.origin_file.handler.get_absolute_path().parent))
        if not f:
            return
        pixmap = QtGui.QPixmap()
        pixmap.load(f)
        if pixmap.width() > pixmap.height():
            pixmap = pixmap.scaledToWidth(20)
        else:
            pixmap = pixmap.scaledToHeight(20)
        pixmap.setDevicePixelRatio(self.devicePixelRatio())
        self.iconLabel.setPixmap(pixmap)
        self.icon = self.origin_file.handler.pixmap_to_b64(pixmap)


class BaseWidget(abc.ABC):
    def __init__(self, file: File) -> None:
        self.file = file
        self.path: str = file.path

    @abc.abstractmethod
    def setupUi(self, widget):
        pass

    def confirm_path(self):
        # please ensure path is true, I will use it later
        pass
