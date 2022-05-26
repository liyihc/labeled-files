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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QLineEdit,
    QListView, QListWidget, QListWidgetItem, QMainWindow,
    QMenu, QMenuBar, QPushButton, QSizePolicy,
    QSpacerItem, QStatusBar, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(725, 511)
        self.openWorkSpaceAction = QAction(MainWindow)
        self.openWorkSpaceAction.setObjectName(u"openWorkSpaceAction")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.searchLineEdit = QLineEdit(self.centralwidget)
        self.searchLineEdit.setObjectName(u"searchLineEdit")

        self.horizontalLayout.addWidget(self.searchLineEdit)

        self.clearTagPushButton = QPushButton(self.centralwidget)
        self.clearTagPushButton.setObjectName(u"clearTagPushButton")

        self.horizontalLayout.addWidget(self.clearTagPushButton)

        self.searchPushButton = QPushButton(self.centralwidget)
        self.searchPushButton.setObjectName(u"searchPushButton")

        self.horizontalLayout.addWidget(self.searchPushButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.treeWidget = QTreeWidget(self.centralwidget)
        self.treeWidget.setObjectName(u"treeWidget")
        self.treeWidget.setMaximumSize(QSize(300, 16777215))
        self.treeWidget.setExpandsOnDoubleClick(False)
        self.treeWidget.header().setCascadingSectionResizes(False)
        self.treeWidget.header().setDefaultSectionSize(200)

        self.horizontalLayout_2.addWidget(self.treeWidget)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tagListWidget = QListWidget(self.centralwidget)
        self.tagListWidget.setObjectName(u"tagListWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tagListWidget.sizePolicy().hasHeightForWidth())
        self.tagListWidget.setSizePolicy(sizePolicy)
        self.tagListWidget.setMaximumSize(QSize(16777215, 40))
        self.tagListWidget.setFlow(QListView.LeftToRight)

        self.verticalLayout.addWidget(self.tagListWidget)

        self.fileVerticalLayout = QVBoxLayout()
        self.fileVerticalLayout.setObjectName(u"fileVerticalLayout")

        self.verticalLayout.addLayout(self.fileVerticalLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.delPushButton = QPushButton(self.centralwidget)
        self.delPushButton.setObjectName(u"delPushButton")

        self.horizontalLayout_3.addWidget(self.delPushButton)


        self.verticalLayout.addLayout(self.horizontalLayout_3)


        self.horizontalLayout_2.addLayout(self.verticalLayout)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 725, 22))
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName(u"menu")
        self.addFileMenu = QMenu(self.menubar)
        self.addFileMenu.setObjectName(u"addFileMenu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.addFileMenu.menuAction())
        self.menu.addAction(self.openWorkSpaceAction)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Labeled files", None))
        self.openWorkSpaceAction.setText(QCoreApplication.translate("MainWindow", u"\u6253\u5f00\u5de5\u4f5c\u533a", None))
        self.searchLineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u641c\u7d22\u6587\u5b57", None))
        self.clearTagPushButton.setText(QCoreApplication.translate("MainWindow", u"\u6d88\u9664\u6807\u7b7e", None))
        self.searchPushButton.setText(QCoreApplication.translate("MainWindow", u"\u641c\u7d22", None))
#if QT_CONFIG(shortcut)
        self.searchPushButton.setShortcut(QCoreApplication.translate("MainWindow", u"Return", None))
#endif // QT_CONFIG(shortcut)
        ___qtreewidgetitem = self.treeWidget.headerItem()
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("MainWindow", u"\u8ba1\u6570", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"\u6807\u7b7e", None));
        self.delPushButton.setText(QCoreApplication.translate("MainWindow", u"\u5220\u9664", None))
#if QT_CONFIG(shortcut)
        self.delPushButton.setShortcut(QCoreApplication.translate("MainWindow", u"Del", None))
#endif // QT_CONFIG(shortcut)
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"\u6587\u4ef6", None))
        self.addFileMenu.setTitle(QCoreApplication.translate("MainWindow", u"\u65b0\u589e\u8bb0\u5f55", None))
    # retranslateUi

