import dataclasses
from datetime import datetime
import os
import platform
import re
from typing import Literal
from urllib.parse import quote, unquote
from PySide6 import QtWidgets, QtCore, QtGui
from pathlib import Path

from labeled_files.setting import setting

from ..base import BasePathHandler, File
import subprocess
from .vscodeUiPy import Widget

vscode_instance_path: Path = None
folder_pixmap: QtGui.QPixmap = None
folder_icon: QtGui.QIcon = None
remote_pixmap: QtGui.QPixmap = None
remote_icon: QtGui.QIcon = None


# file+file://...
# folder+file://...
# workspace+remote://...

template = re.compile(
    r"^(file|folder|workspace)\+(file|vscode-remote)://(.*)")


@dataclasses.dataclass
class VscodePath:
    typ: Literal["file", "folder", "workspace"]
    protocol: Literal["file", "vscode-remote"]
    remote_host: str
    path: str

    def to_str(self):
        return f"{self.typ}+{self.to_vscode_cli()}"

    def to_vscode_cli(self):
        if self.protocol == "vscode-remote":
            assert self.remote_host
            path = f"ssh-remote+{self.remote_host}{self.path}"
            return f"{self.protocol}://{quote(path)}"
        if self.protocol == "file":
            return f"{self.protocol}://{quote(self.path)}"

    @classmethod
    def from_str(self, s: str):
        result = template.match(s)
        if not result:
            return VscodePath("file", "file", "", "")
        vp = VscodePath(result.group(1), result.group(2), "", "")
        path = unquote(result.group(3))
        if vp.protocol == "vscode-remote":
            path = path.removeprefix("ssh-remote+")
            ind = path.find('/')
            vp.remote_host, vp.path = path[:ind], path[ind:]
        elif vp.protocol == "file":
            vp.path = path
        return vp


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
            vp = VscodePath.from_str(self.file.path)
            if vp.protocol == "file":
                path = vp.path
                if platform.system() == "Windows":
                    path = path.removeprefix('/')
                    path = str(setting.convert_path(Path(path)))
                    path = '/' + path
                else:
                    path = str(setting.convert_path(Path(path)))
                vp.path = path

            if vp.typ == "file" or vp.typ == "workspace":
                subprocess.Popen(
                    [str(vscode_instance_path), '--file-uri', vp.to_vscode_cli()],
                    shell=True,
                    env=setting.get_clean_env(),
                    cwd=Path.home()
                    )
            else:  # vp.type == "workspace"
                subprocess.Popen(
                    [str(vscode_instance_path),
                     '--folder-uri', vp.to_vscode_cli()],
                    shell=True,
                    env=setting.get_clean_env(),
                    cwd=Path.home()
                    )

    def get_widget_type(self):
        return Widget

    def open_path(self):
        if self.file.path:
            vp = VscodePath.from_str(self.file.path)
            if vp.protocol == "file":
                path = vp.path
                if platform.system() == "Windows":
                    path = Path(path.removeprefix('/'))
                    path = setting.convert_path(path)
                    subprocess.Popen(
                        f'explorer /select,"{path}"')
                # else:
                #     path = setting.convert_path(path)
                #     pass

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

    def actual_name_get(self) -> str:
        return self.file.path