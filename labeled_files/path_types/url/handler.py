from datetime import datetime
import webbrowser
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
        from .webUiPy import Dialog as WebDialog
        dialog = WebDialog(mime_path)
        dialog.show()
        dialog.exec()
        if not dialog.url_accept:
            return
        title = dialog.windowTitle()
        pixmap = cls.icon_to_pixmap(dialog.windowIcon())
        if pixmap is not None and pixmap.width() > 32:
            pixmap = pixmap.scaled(32, 32)
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
        from .webUiPy import Dialog as WebDialog
        dialog = WebDialog(self.file.path)
        dialog.show()
        dialog.exec()
        if not dialog.url_accept:
            return
        return dialog.windowIcon()

    def open(self):
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
