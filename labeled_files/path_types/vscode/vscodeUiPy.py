from ..fileUiPy import BaseWidget
from .vscodeUi import Ui_Form
from . import handler


class Widget(BaseWidget, Ui_Form):
    def setupUi(self, widget):
        self.widget = widget
        Ui_Form.setupUi(self, widget)

        self.localRadioButton.clicked.connect(self.radio_change)
        self.sshRadioButton.clicked.connect(self.radio_change)
        self.wslRadioButton.clicked.connect(self.radio_change)
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

        match vp.protocol:
            case "local":
                self.localRadioButton.setChecked(True)
            case "ssh":
                self.sshRadioButton.setChecked(True)
            case "wsl":
                self.wslRadioButton.setChecked(True)
        self.hostLineEdit.setText(vp.host)
        self.pathLineEdit.setText(vp.path)

    def radio_change(self):
        if self.localRadioButton.isChecked():
            self.hostLineEdit.setEnabled(False)
        else:
            self.hostLineEdit.setEnabled(True)

    def confirm_path(self):
        if self.localRadioButton.isChecked():
            protocol = "local"
            host = ""
            path = self.pathLineEdit.text().replace("\\", "/")
            if not path.startswith("/"):
                path = '/' + path
        else:
            host = self.hostLineEdit.text()
            path = self.pathLineEdit.text()
            if self.sshRadioButton.isChecked():
                protocol = "ssh"
            elif self.wslRadioButton.isChecked():
                protocol = "wsl"
        if self.fileRadioButton.isChecked():
            typ = "file"
        elif self.folderRadioButton.isChecked():
            typ = "folder"
        elif self.workspaceRadioButton.isChecked():
            typ = "workspace"
        vp = handler.VscodePath(typ, protocol, host, path)
        self.path = vp.to_str()
