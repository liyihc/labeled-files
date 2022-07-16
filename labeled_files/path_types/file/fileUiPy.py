from PySide6.QtWidgets import QFileDialog
from .fileUi import Ui_Form
from ..fileUiPy import BaseWidget


class Widget(BaseWidget, Ui_Form):
    def setupUi(self, widget):
        self.widget = widget
        Ui_Form.setupUi(self, widget)
        self.pushButton.clicked.connect(self.change_path)

    def change_path(self):
        if self.file.type == "file":
            f, typ = QFileDialog.getOpenFileName(
                self.widget, "choose a file",
                str(self.file.handler.get_absolute_path().parent))
        else:
            f = QFileDialog.getExistingDirectory(self.widget, "choose a folder", str(
                self.file.handler.get_absolute_path().parent))
        if not f:
            return
        self.path = f
