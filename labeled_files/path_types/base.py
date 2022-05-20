
import abc
import base64
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Type
from PySide6.QtGui import QIcon, QPixmap, QScreen
from PySide6.QtCore import QFileInfo, QByteArray, QBuffer, QIODevice
from ..setting import Setting

path_handler_factories: Dict[str, Type['BasePathHandler']] = {}


@dataclass
class _File:
    id: int
    name: str
    type: str
    path: str
    tags: List[str]
    ctime: datetime
    icon: str
    description: str


class File(_File):
    handler: 'HandlerDescriptor'


class HandlerDescriptor:
    def __init__(self, setting: Setting) -> None:
        self.setting = setting

    def __get__(self, obj, objtype=None) -> 'BasePathHandler':
        if isinstance(obj, File):
            return path_handler_factories[obj.type](self.setting, obj)
        return self


class BasePathHandler(abc.ABC):
    def __init__(self, setting: Setting, file: File) -> None:
        self.setting = setting
        self.file = file

    @classmethod
    def init_var(cls):
        pass

    @staticmethod
    def icon_to_pixmap(icon: QIcon):
        return icon.pixmap(20, 20)

    @staticmethod
    def pixmap_to_b64(pixmap: QPixmap):
        b = QByteArray()
        buffer = QBuffer(b)
        buffer.open(QIODevice.WriteOnly)
        pixmap.save(buffer, 'PNG')
        buffer.close()
        return base64.b64encode(b.data())

    @staticmethod
    def icon_to_b64(icon: QIcon):
        return BasePathHandler.pixmap_to_b64(BasePathHandler.icon_to_pixmap(icon))

    @classmethod
    @abc.abstractmethod
    def mime_acceptable(cls, mime_path: str) -> bool:
        pass

    @classmethod
    @abc.abstractmethod
    def create_file_from_mime(cls, mime_path: str) -> File:
        pass

    @classmethod
    @abc.abstractmethod
    def create_file(cls) -> File:
        pass

    @abc.abstractmethod
    def copy_to(self):
        pass

    @abc.abstractmethod
    def move_to(self):
        pass

    @abc.abstractmethod
    def get_default_icon(self) -> QIcon:
        pass

    @abc.abstractmethod
    def open(self):
        pass

    @abc.abstractmethod
    def edit(self, callback):
        pass

    @abc.abstractmethod
    def open_path(self):
        pass

    @abc.abstractmethod
    def repr(self) -> str:
        pass

    @abc.abstractmethod
    def remove(self):
        pass

    def get_icon(self) -> QIcon:
        if self.file.icon:
            pixmap = QPixmap()
            pixmap.loadFromData(base64.b64decode(self.file.icon))
            return QIcon(pixmap)
        return self.get_default_icon()

    def get_pixmap(self) -> QPixmap:
        if self.file.icon:
            pixmap = QPixmap()
            pixmap.loadFromData(base64.b64decode(self.file.icon))
            return pixmap
        return self.icon_to_pixmap(self.get_default_icon())
