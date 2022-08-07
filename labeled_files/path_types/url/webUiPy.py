from PySide6 import QtWidgets, QtCore, QtGui
from .webUi import Ui_Dialog


class Dialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, path:str) -> None:
        super().__init__()
        self.setupUi(self)

        style = self.style()
        self.refreshToolButton.setIcon(
            style.standardIcon(style.SP_BrowserReload))
        self.stopToolButton.setIcon(style.standardIcon(style.SP_BrowserStop))
        self.gotoToolButton.setIcon(style.standardIcon(style.SP_CommandLink))

        self.lineEdit.keyPressEvent = self.lineedit_keyPressEvent
        self.refreshToolButton.clicked.connect(self.webEngineView.reload)
        self.stopToolButton.clicked.connect(self.webEngineView.stop)
        self.gotoToolButton.clicked.connect(self.goto)
        self.webEngineView.urlChanged.connect(self.url_changed)
        self.webEngineView.titleChanged.connect(self.setWindowTitle)
        self.webEngineView.iconChanged.connect(self.setWindowIcon)

        self.url_accept = False

        self.lineEdit.setText(path)
        self.goto()

    def goto(self):
        url = self.lineEdit.text()
        if "://" not in url:
            url = f"http://{url}"
        self.webEngineView.setUrl(url)

    def lineedit_keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        if e.key() == QtCore.Qt.Key_Return or e.key() == QtCore.Qt.Key_Enter:
            self.gotoToolButton.click()
            return
        QtWidgets.QLineEdit.keyPressEvent(self.lineEdit, e)

    def url_changed(self, url: QtCore.QUrl):
        if not self.lineEdit.hasFocus():
            self.lineEdit.setText(url.url())

    def accept(self) -> None:
        self.url_accept = True
        return super().accept()