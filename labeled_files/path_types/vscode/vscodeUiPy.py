from urllib.parse import quote, unquote

from ..fileUiPy import BaseWidget
from .vscodeUi import Ui_Form
from . import handler


class Widget(BaseWidget, Ui_Form):
    def setupUi(self, widget):
        self.widget = widget
        Ui_Form.setupUi(self, widget)

        self.localRadioButton.clicked.connect(self.radio_change)
        self.remoteRadioButton.clicked.connect(self.radio_change)
        p = self.path
        if not p:
            return
        vp = handler.VscodePath.from_str(p)
        match vp.typ:
            case "file":
                self.fileRadioButton.setChecked(True)
            case "folder":
                self.folderRadioButton.setChecked(True)
            case "workspace":
                self.workspaceRadioButton.setChecked(True)
        if vp.protocol == "file":
            self.localRadioButton.setChecked(True)
            self.localLineEdit.setText(vp.path)
        else:
            self.remoteRadioButton.setChecked(True)
            self.remoteHostLineEdit.setText(vp.remote_host)
            self.remotePathLineEdit.setText(vp.path)

    def radio_change(self):
        if self.localRadioButton.isChecked():
            self.localLineEdit.setEnabled(True)
            self.remoteHostLineEdit.setEnabled(False)
            self.remotePathLineEdit.setEnabled(False)
        else:
            self.localLineEdit.setEnabled(False)
            self.remoteHostLineEdit.setEnabled(True)
            self.remotePathLineEdit.setEnabled(True)

    def confirm_path(self):
        if self.localRadioButton.isChecked():
            protocol = "file"
            host = ""
            path = self.localLineEdit.text().replace("\\", "/")
            if not path.startswith("/"):
                path = '/' + path
        else:
            host = self.remoteHostLineEdit.text()
            path = self.remotePathLineEdit.text()
            protocol = "vscode-remote"
        if self.fileRadioButton.isChecked():
            typ = "file"
        elif self.folderRadioButton.isChecked():
            typ = "folder"
        elif self.workspaceRadioButton.isChecked():
            typ = "workspace"
        vp = handler.VscodePath(typ, protocol, host, path)
        self.path = vp.to_str()
