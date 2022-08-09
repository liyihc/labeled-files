from datetime import datetime
from ..base import BasePathHandler, File
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QInputDialog


class Handler(BasePathHandler):
    support_dynamic_icon = False

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
        title, pixmap = get_from_url(mime_path)
        if not title:
            title = mime_path.removeprefix("http://").removeprefix("https://")
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

    def get_default_icon(self) -> QIcon | None:
        _, pixmap = get_from_url(self.file.path)
        if pixmap is not None:
            return QIcon(pixmap)

    def open(self):
        import webbrowser
        webbrowser.open(self.file.path)

    def get_widget_type(self):
        from .urlUiPy import Widget
        return Widget

    def open_path(self):
        pass

    def repr(self) -> str:
        return f"url: {self.file.path}"

    def remove(self):
        pass

    def actual_name_get(self) -> str:
        return self.file.path


def get_from_url(url: str):
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urlparse
    ret = requests.get(url, timeout=2)
    soup = BeautifulSoup(ret.content)

    soup = BeautifulSoup(ret.content)
    title = soup.title

    icon_link = soup.find("link", rel="shortcut icon")
    if icon_link is None:
        icon_link = soup.find("link", rel="icon")

    if icon_link is not None:
        icon_url = icon_link["href"].removeprefix('/')
        if not icon_url.startswith("http"):
            icon_url = f"{url}/{icon_url}"
    else:
        parse_result = urlparse(url)
        icon_url = f"{parse_result.scheme}://{parse_result.netloc}/favicon.ico"
    ret = requests.get(icon_url)
    if ret.status_code == 200:
        pixmap = QPixmap()
        pixmap.loadFromData(ret.content)
    else:
        pixmap = None

    if pixmap is not None and pixmap.width() > 32:
        pixmap = pixmap.scaled(32, 32)
    return title, pixmap
