from datetime import datetime
from multiprocessing import Process
import shutil
import subprocess
import random
from pathlib import Path
from PySide6.QtCore import QFileInfo, QByteArray, QBuffer, QIODevice
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileIconProvider, QMessageBox, QInputDialog
from labeled_files.setting import setting

from ..base import BasePathHandler, File

from .fileUiPy import Widget

need_icon_suffixes = {".exe", "", ".lnk"}
EXECUTABLE = {".exe"}


icon_provider: QFileIconProvider = None


class Handler(BasePathHandler):
    @classmethod
    def init_var(cls):
        global icon_provider
        icon_provider = QFileIconProvider()
        return True

    @classmethod
    def mime_acceptable(cls, mime_path: str) -> bool:
        return mime_path.startswith("file:///")

    @classmethod
    def create_file_from_mime(cls, mime_path: str) -> File:
        p = Path(mime_path.removeprefix("file:///"))
        stat = p.stat()
        typ = "folder" if p.is_dir() else "file"
        f = File(None, p.name, typ, str(p), [], datetime.fromtimestamp(
            stat.st_ctime), datetime.now(), "", "")
        if typ == "file" and p.suffix.lower() in need_icon_suffixes:
            icon = f.handler.get_default_icon()
            f.icon = f.handler.icon_to_b64(icon)
        else:
            # generate icon for folder or file.type dynamicly
            pass
        return f

    @classmethod
    def create_file_able(cls, handler_type) -> bool:
        return handler_type == "folder"

    @classmethod
    def create_file(cls, handler_type) -> File | None:
        assert handler_type == "folder"
        text, ok = QInputDialog.getText(None, "文件夹名", "请为新文件夹输入名称")
        if not ok:
            return
        f = File(None, text, "folder", text, [],
                 datetime.now(), datetime.now(), "", "")
        path_rel: Path
        path_abs: Path
        path_rel, path_abs = f.handler.get_new_name()
        path_abs.mkdir()
        f.path = str(path_rel)
        return f

    def get_new_name(self):
        """
            return relative, absolute
        """
        p = Path(self.file.path)
        while True:
            target_p = setting.root_path.joinpath(
                f"{p.stem} {datetime.now().strftime('%y-%m-%d %H_%M_%S')} {format(random.randint(0,9999), '05d')}{p.suffix}")
            if not target_p.exists():
                break
        return target_p.relative_to(setting.root_path), target_p

    def copy_to(self):
        p = Path(self.file.path)
        target_rel, target_abs = self.get_new_name()
        if p.is_dir():
            shutil.copytree(p, target_abs)
        else:
            shutil.copy(p, target_abs)
        self.file.path = str(target_rel)

    def move_to(self):
        p = Path(self.file.path)
        target_rel, target_abs = self.get_new_name()
        shutil.move(p, target_abs)
        self.file.path = str(target_rel)

    def get_default_icon(self) -> QIcon:
        if self.file.type == "folder":
            return icon_provider.icon(icon_provider.IconType.Folder)
        path = self.get_absolute_path()
        if path.suffix.lower() in need_icon_suffixes:
            return icon_provider.icon(QFileInfo(path))
        else:
            return icon_provider.icon(QFileInfo(path.name))

    def get_absolute_path(self) -> Path:
        path = Path(self.file.path)
        if path.is_absolute():
            path = setting.convert_path(path)
        return setting.root_path.joinpath(path)

    def open(self):
        p = self.get_absolute_path()
        if p.exists():
            process = Process(target=open_file, args=(p, setting.get_clean_env()))
            process.start()
            process.join()
        else:
            QMessageBox.information(None, "文件不存在", str(p))  # or raise error

    def get_widget_type(self):
        return Widget

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
                if p.is_dir():
                    shutil.rmtree(p)
                else:
                    p.unlink()

def open_file(path:Path, env: dict):
    import os

    os.chdir(path.parent)
    for k in os.environ:
        if k not in env:
            os.environ.pop(k)
    for k, v in env.items():
        os.environ[k] = v
    os.startfile(path)