
import abc
import base64
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Type
import weakref
from PySide6.QtGui import QIcon, QPixmap, QScreen
from PySide6.QtCore import QFileInfo, QByteArray, QBuffer, QIODevice

path_handler_types: Dict[str, Type['BasePathHandler']] = {}


@dataclass
class _File:
    id: int
    name: str
    type: str
    path: str
    tags: List[str]
    ctime: datetime
    vtime: datetime
    icon: str
    description: str


class File(_File):
    handler: 'HandlerDescriptor'  # class attribute


class HandlerDescriptor:
    def __get__(self, obj, objtype=None) -> 'BasePathHandler':
        if isinstance(obj, File):
            return path_handler_types[obj.type](obj)
        return self


class BasePathHandler(abc.ABC):
    support_custom_duplicate = False

    def __init__(self, file: File) -> None:
        self.file: File = weakref.proxy(file)
        self.win = None

    @classmethod
    def init_var(cls) -> bool:
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
    def create_file_able(cls, handler_name: str) -> bool:
        pass

    @classmethod
    @abc.abstractmethod
    def create_file(cls, handler_name: str) -> File:
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

    def edit(self, callback):
        from .fileUiPy import Window
        if self.win is not None:
            self.win.show()
        else:
            win = self.win = Window(
                self.get_widget_type()(self.file), self.file)
            win.show()
            win.reshow.connect(callback)

    @abc.abstractmethod
    def open_path(self):
        pass

    @abc.abstractmethod
    def get_widget_type(self):
        '''
            Type[.fileUiPy.BaseWidget]
        '''
        pass

    @abc.abstractmethod
    def repr(self) -> str:
        pass

    @abc.abstractmethod
    def remove(self):
        pass

    @abc.abstractmethod
    def actual_name_get(self) -> str:
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

    def custom_deplicate(self) -> File:
        pass
