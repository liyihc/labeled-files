from datetime import datetime
import os
import webbrowser
from ..base import BasePathHandler, File
import requests
from bs4 import BeautifulSoup
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QInputDialog
from .urlUiPy import Widget


class Handler(BasePathHandler):
    @classmethod
    def init_var(cls) -> bool:
        return True

    @classmethod
    def mime_acceptable(cls, mime_path: str) -> bool:
        """
        http or https
        """
        return mime_path.startswith("http")

    @classmethod
    def create_file_from_mime(cls, mime_path: str) -> File:
        mime_path = mime_path.removesuffix('/')
        ret = requests.get(mime_path, timeout=2)
        soup = BeautifulSoup(ret.content)
        title = soup.title
        if title:
            title = soup.title.text
        else:
            title = mime_path.removeprefix("http://").removeprefix("https://")
        pixmap = get_icon_from_url(mime_path, soup)
        if pixmap is not None and pixmap.width() > 20:
            pixmap = pixmap.scaled(20, 20)
        return File(
            None,
            title or mime_path,
            "url",
            mime_path,
            [],
            datetime.now(),
            datetime.now(),
            cls.pixmap_to_b64(pixmap),
            ""
        )

    @classmethod
    def create_file_able(cls, handler_name: str) -> bool:
        return handler_name == "url"

    @classmethod
    def create_file(cls, handler_name: str) -> File:
        assert handler_name == "url"
        text: str
        text, ok = QInputDialog.getText(None, "url", "请输入新url")
        if not ok:
            return
        assert text.startswith("http"), "请指定http或https"
        return cls.create_file_from_mime(text)

    def copy_to(self):
        pass

    def move_to(self):
        pass

    def get_default_icon(self) -> QIcon:
        return QIcon(get_icon_from_url(self.file.path))

    def open(self):
        webbrowser.open(self.file.path)

    def get_widget_type(self):
        return Widget

    def open_path(self):
        pass

    def repr(self) -> str:
        return f"url: {self.file.path}"

    def remove(self):
        pass

    def actual_name_get(self) -> str:
        return self.file.path


def get_icon_from_url(domain: str, soup: BeautifulSoup = None):
    if not soup:
        ret = requests.get(domain, timeout=2)
        soup = BeautifulSoup(ret.content)

    icon_link = soup.find("link", rel="shortcut icon")
    if icon_link is None:
        icon_link = soup.find("link", rel="icon")
    if icon_link is None:
        icon_url = f"{domain}/favicon.ico"
    else:
        icon_url = icon_link["href"].removeprefix('/')
        if not icon_url.startswith("http"):
            icon_url = f"{domain}/{icon_url}"
    ret = requests.get(icon_url)
    if ret.status_code != 200:
        return None

    pixmap = QPixmap()
    pixmap.loadFromData(ret.content)
    return pixmap
