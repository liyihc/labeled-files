import dataclasses
from datetime import datetime
import os
import platform
import re
from typing import Literal
from PySide6 import QtWidgets, QtCore, QtGui
from pathlib import Path

from labeled_files.setting import setting

from ..base import BasePathHandler, File
import subprocess

vscode_instance_path: Path = None
folder_pixmap: QtGui.QPixmap = None
folder_icon: QtGui.QIcon = None
remote_pixmap: QtGui.QPixmap = None
remote_icon: QtGui.QIcon = None


# file+file://...
# folder+file://...
# workspace+vscode-remote://ssh-remote+hostname/path
# folder+vscode-remote://wsl+hostname/path


template = re.compile(
    r"^(file|folder|workspace)\+(file|vscode-remote)://(.*)")


@dataclasses.dataclass
class VscodePath:
    typ: Literal["file", "folder", "workspace"]
    protocol: Literal["local", "ssh", "wsl"]
    host: str
    path: str

    def to_str(self):
        return f"{self.typ}+{self.to_vscode_cli()}"

    def to_vscode_cli(self):
        from urllib.parse import quote
        if self.protocol == "local":
            return f"file://{quote(self.path)}"
        assert self.host
        if self.protocol == "ssh":
            path = f"ssh-remote+{self.host}{self.path}"
        elif self.protocol == "wsl":
            path = f"wsl+{self.host}{self.path}"
        return f"vscode-remote://{quote(path)}"

    @classmethod
    def from_str(self, s: str):
        from urllib.parse import unquote
        result = template.match(s)
        if not result:
            return VscodePath("file", "local", "", "")
        vp = VscodePath(result.group(1), "", "", "")
        is_local = result.group(2) == "file"
        path = unquote(result.group(3))
        if is_local:
            vp.protocol = "local"
            vp.path = path
        else:
            if path.startswith("ssh-remote"):
                vp.protocol = "ssh"
                path = path.removeprefix("ssh-remote+")
                ind = path.find('/')
                vp.host, vp.path = path[:ind], path[ind:]
            elif path.startswith("wsl"):
                vp.protocol = "wsl"
                path = path.removeprefix("wsl+")
                ind = path.find('/')
                vp.host, vp.path = path[:ind], path[ind:]
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
                folder_pixmap = remote_pixmap = icon.pixmap(32, 32)
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
            if vp.protocol == "local":
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
        from .vscodeUiPy import Widget
        return Widget

    def get_absolute_path(self) -> Path:
        if self.file.path:
            vp = VscodePath.from_str(self.file.path)
            if vp.protocol == "local":
                path = vp.path
                if platform.system() == "Windows":
                    path = Path(path.removeprefix('/'))
                    return setting.convert_path(path)
        return super().get_absolute_path()

    def open_path(self):
        path = self.get_absolute_path()
        if path == Path.home():
            return
        subprocess.Popen(f'explorer /select,"{path}"')

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
