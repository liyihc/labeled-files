from .urlUi import Ui_Form
from ..fileUiPy import BaseWidget

class Widget(BaseWidget, Ui_Form):
    def setupUi(self, widget):
        self.widget = widget
        Ui_Form.setupUi(self, widget)

        self.lineEdit.setText(self.file.path)

    def confirm_path(self):
        self.path  = self.lineEdit.text()