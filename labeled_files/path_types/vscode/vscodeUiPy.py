from urllib.parse import quote, unquote
from ..fileUiPy import BaseWidget
from .vscodeUi import Ui_Form


class Widget(BaseWidget, Ui_Form):
    def setupUi(self, widget):
        self.widget = widget
        Ui_Form.setupUi(self, widget)

        self.localRadioButton.clicked.connect(self.radio_change)
        self.remoteRadioButton.clicked.connect(self.radio_change)
        p = self.path
        if not p:
            return
        prefix, p = p.split("+", 1)
        match prefix:
            case "file":
                self.fileRadioButton.setChecked(True)
            case "folder":
                self.folderRadioButton.setChecked(True)
            case "workspace":
                self.workspaceRadioButton.setChecked(True)
        if p.startswith("file"):
            self.localRadioButton.setChecked(True)
            self.localLineEdit.setText(
                unquote(p.removeprefix("file://")))
        else:
            self.remoteRadioButton.setChecked(True)
            p = unquote(self.path.removeprefix(
                "vscode-remote://ssh-remote+")).split("/", 1)
            self.remoteHostLineEdit.setText(p[0])
            self.remotePathLineEdit.setText('/' + p[1])

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
        path = ""
        if self.localRadioButton.isChecked():
            if self.localLineEdit.text():
                path = self.localLineEdit.text()
                path = path.replace("\\", "/")
                if not path.startswith("/"):
                    path = '/' + path
                path = "file://" + quote(path)
        else:
            host = self.remoteHostLineEdit.text()
            r_path = self.remotePathLineEdit.text()
            if host and r_path:
                path = "vscode-remote://" + \
                    quote(f"ssh-remote+{host}{r_path}")
        if path:
            if self.fileRadioButton.isChecked():
                prefix = "file"
            elif self.folderRadioButton.isChecked():
                prefix = "folder"
            elif self.workspaceRadioButton.isChecked():
                prefix = "workspace"
            path = f"{prefix}+{path}"
        self.path = path
