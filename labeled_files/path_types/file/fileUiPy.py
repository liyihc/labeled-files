from pathlib import Path
from PySide6.QtWidgets import QFileDialog
from ..base import File
from .fileUi import Ui_Form
from ..fileUiPy import BaseWidget


class Widget(BaseWidget, Ui_Form):
    def setupUi(self, widget):
        self.widget = widget
        Ui_Form.setupUi(self, widget)
        self.pushButton.clicked.connect(self.change_path)

    def change_path(self):
        f, typ = QFileDialog.getOpenFileName(
            self.widget, "choose a file",
            str(self.file.handler.get_absolute_path().parent))
        if not f:
            return
        self.path = f
