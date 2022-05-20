from base64 import b64encode
from datetime import datetime
import os
import shutil
import subprocess
import random
from pathlib import Path
from types import ClassMethodDescriptorType
from PySide6.QtCore import QFileInfo, QByteArray, QBuffer, QIODevice
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileIconProvider, QMessageBox
from ..base import BasePathHandler, File, Setting

from .fileUiPy import Window

need_icon_suffixes = {".exe", "", ".lnk"}


icon_provider: QFileIconProvider = None


class Handler(BasePathHandler):
    def __init__(self, setting: Setting, file: File) -> None:
        super().__init__(setting, file)
        self.win: Window = None

    @classmethod
    def init_var(cls):
        global icon_provider
        icon_provider = QFileIconProvider()

    @classmethod
    def mime_acceptable(cls, mime_path: str) -> bool:
        return mime_path.startswith("file:///")

    @classmethod
    def create_file_from_mime(cls, mime_path: str) -> File:
        p = Path(mime_path.removeprefix("file:///"))
        stat = p.stat()
        typ = "folder" if p.is_dir() else "file"
        f = File(None, p.name, typ, str(p), [], datetime.fromtimestamp(
            stat.st_ctime), "", "")
        if typ == "file" and p.suffix.lower() in need_icon_suffixes:
            icon = f.handler.get_default_icon()
            f.icon = f.handler.icon_to_b64(icon)
        else:
            # generate icon for folder or file.type dynamicly
            pass
        return f

    @classmethod
    def create_file(self) -> File:
        # 其他类型可能会需要创建file
        return super().create_file()

    def copy_to(self):
        p = Path(self.file.path)
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
        self.file.path = str(target_p)

    def move_to(self):
        p = Path(self.file.path)
        while True:
            target_p = self.setting.root_path.joinpath(
                f"{p.stem} {datetime.now().strftime('%y-%m-%d %H_%M_%S')} {format(random.randint(0,9999), '05d')}{p.suffix}")
            if not target_p.exists():
                break
        shutil.move(p, target_p)
        target_p = target_p.relative_to(self.setting.root_path)
        self.file.path = str(target_p)

    def get_default_icon(self) -> QIcon:
        if self.file.type == "folder":
            return icon_provider.icon(icon_provider.IconType.Folder)
        return icon_provider.icon(QFileInfo(Path(self.file.path).name))

    def get_absolute_path(self) -> Path:
        path = Path(self.file.path)
        if path.is_absolute():
            return path
        return self.setting.root_path.joinpath(path)

    def open(self):
        p = self.get_absolute_path()
        if p.exists():
            cwd = os.getcwd()
            os.chdir(p.parent)
            os.startfile(p)
            os.chdir(cwd)
        else:
            QMessageBox.information(None, "文件不存在", str(p))  # or raise error

    def edit(self, callback):
        if self.win is not None:
            self.win.show()
        else:
            win = self.win = Window(self.setting, self.file)
            win.show()
            win.reshow.connect(callback)

        return super().edit(callback)

    def open_path(self):
        subprocess.Popen(
            f'explorer /select,"{self.get_absolute_path()}"')

    def repr(self) -> str:
        p = Path(self.file.path)
        if p.is_absolute():
            return f"file: link-to: {self.file.name}"
        else:
            return f"file: {self.file.name}"

    def remove(self):
        if not Path(self.file.path).is_absolute():
            p = self.get_absolute_path()
            if p.exists():
                p.unlink()
