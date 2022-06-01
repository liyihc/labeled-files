from datetime import datetime
import os
from PySide6 import QtWidgets, QtCore, QtGui
from pathlib import Path

from ..base import BasePathHandler, File
import subprocess
from .vscodeUiPy import Widget

vscode_instance_path: Path = None
folder_pixmap: QtGui.QPixmap = None
folder_icon: QtGui.QIcon = None
remote_pixmap: QtGui.QPixmap = None
remote_icon: QtGui.QIcon = None


class Handler(BasePathHandler):
    @classmethod
    def init_var(cls) -> bool:
        global vscode_instance_path, folder_pixmap, remote_pixmap, folder_icon, remote_icon
        for p in os.getenv("PATH").split(";"):
            if "VS Code" in p:
                vscode_instance_path = Path(p).parent / "Code.exe"
                # pix = QPixmap()
                # pix.load(p.)
                # 原程序是获得一个文件夹然后叠加起来，奇才
                icon_provider = QtWidgets.QFileIconProvider()
                icon = icon_provider.icon(
                    QtCore.QFileInfo(vscode_instance_path))
                folder_icon = remote_icon = icon
                folder_pixmap = remote_pixmap = icon.pixmap(20, 20)
                return True
        return False

    @classmethod
    def mime_acceptable(cls, mime_path: str) -> bool:
        return False

    @classmethod
    def create_file_from_mime(cls, mime_path: str):
        raise NotImplementedError()

    @classmethod
    def create_file_able(cls, handler_name: str) -> bool:
        return True

    @classmethod
    def create_file(cls, handler_name: str) -> File:
        return File(None, "新工作区", "vscode", "", [], datetime.now(), datetime.now(), cls.pixmap_to_b64(folder_pixmap), "")

    def copy_to(self):
        raise NotImplementedError()

    def move_to(self):
        raise NotImplementedError()

    def get_default_icon(self) -> QtGui.QIcon:
        return folder_icon

    def open(self):
        if self.file.path:
            prefix, path = self.file.path.split("+", 1)
            if prefix == "file" or prefix == "workspace":
                subprocess.Popen([str(vscode_instance_path), '--file-uri', path])
            else:
                subprocess.Popen([str(vscode_instance_path), '--folder-uri', path])

    def get_widget_type(self):
        return Widget

    def open_path(self):
        pass

    def repr(self) -> str:
        p = self.file.path
        if not p:
            return "vscode: empty"
        prefix, p = p.split("+", 1)
        prefix = [prefix]

        if p.startswith("file:///"):
            prefix.append("Local")
        elif p.startswith("remote://"):
            prefix.append("Remote")
        prefix = ' - '.join(prefix)
        return f"vscode: {prefix} - {self.file.name}"

    def remove(self):
        pass
