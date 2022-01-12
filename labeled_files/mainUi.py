# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.2.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLineEdit,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(445, 511)
        self.openWorkSpaceAction = QAction(MainWindow)
        self.openWorkSpaceAction.setObjectName(u"openWorkSpaceAction")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.searchLineEdit = QLineEdit(self.centralwidget)
        self.searchLineEdit.setObjectName(u"searchLineEdit")

        self.horizontalLayout.addWidget(self.searchLineEdit)

        self.sortComboBox = QComboBox(self.centralwidget)
        self.sortComboBox.setObjectName(u"sortComboBox")

        self.horizontalLayout.addWidget(self.sortComboBox)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.listVerticalLayout = QVBoxLayout()
        self.listVerticalLayout.setObjectName(u"listVerticalLayout")

        self.verticalLayout.addLayout(self.listVerticalLayout)

        self.newFolderPushButton = QPushButton(self.centralwidget)
        self.newFolderPushButton.setObjectName(u"newFolderPushButton")

        self.verticalLayout.addWidget(self.newFolderPushButton)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 445, 22))
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName(u"menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu.menuAction())
        self.menu.addAction(self.openWorkSpaceAction)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Labeled files", None))
        self.openWorkSpaceAction.setText(QCoreApplication.translate("MainWindow", u"\u6253\u5f00\u5de5\u4f5c\u533a", None))
        self.newFolderPushButton.setText(QCoreApplication.translate("MainWindow", u"\u65b0\u5efa\u6587\u4ef6\u5939", None))
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"\u6587\u4ef6", None))
    # retranslateUi

