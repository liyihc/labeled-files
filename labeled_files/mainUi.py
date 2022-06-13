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
from PySide6.QtWidgets import (QApplication, QGroupBox, QHBoxLayout, QHeaderView,
    QLineEdit, QListView, QListWidget, QListWidgetItem,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QStatusBar, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QWidget)

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
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setMaximumSize(QSize(250, 16777215))
        self.verticalLayout_4 = QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.pinTagWidget = QWidget(self.groupBox)
        self.pinTagWidget.setObjectName(u"pinTagWidget")

        self.verticalLayout_4.addWidget(self.pinTagWidget)

        self.tagLineEdit = QLineEdit(self.groupBox)
        self.tagLineEdit.setObjectName(u"tagLineEdit")

        self.verticalLayout_4.addWidget(self.tagLineEdit)

        self.treeWidget = QTreeWidget(self.groupBox)
        self.treeWidget.setObjectName(u"treeWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeWidget.sizePolicy().hasHeightForWidth())
        self.treeWidget.setSizePolicy(sizePolicy)
        self.treeWidget.setMaximumSize(QSize(250, 16777215))
        self.treeWidget.setExpandsOnDoubleClick(False)
        self.treeWidget.header().setCascadingSectionResizes(False)
        self.treeWidget.header().setDefaultSectionSize(180)

        self.verticalLayout_4.addWidget(self.treeWidget)


        self.horizontalLayout_2.addWidget(self.groupBox)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.searchLineEdit = QLineEdit(self.centralwidget)
        self.searchLineEdit.setObjectName(u"searchLineEdit")

        self.horizontalLayout.addWidget(self.searchLineEdit)

        self.clearSearchPushButton = QPushButton(self.centralwidget)
        self.clearSearchPushButton.setObjectName(u"clearSearchPushButton")

        self.horizontalLayout.addWidget(self.clearSearchPushButton)

        self.searchPushButton = QPushButton(self.centralwidget)
        self.searchPushButton.setObjectName(u"searchPushButton")

        self.horizontalLayout.addWidget(self.searchPushButton)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.tagListWidget = QListWidget(self.centralwidget)
        self.tagListWidget.setObjectName(u"tagListWidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.tagListWidget.sizePolicy().hasHeightForWidth())
        self.tagListWidget.setSizePolicy(sizePolicy1)
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
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"\u6807\u7b7e", None))
        self.tagLineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u641c\u7d22\u6807\u7b7e", None))
        ___qtreewidgetitem = self.treeWidget.headerItem()
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("MainWindow", u"\u8ba1\u6570", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"\u6807\u7b7e", None));
        self.searchLineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u641c\u7d22\u6587\u5b57", None))
        self.clearSearchPushButton.setText(QCoreApplication.translate("MainWindow", u"\u6d88\u9664\u6807\u7b7e", None))
        self.searchPushButton.setText(QCoreApplication.translate("MainWindow", u"\u641c\u7d22", None))
#if QT_CONFIG(shortcut)
        self.searchPushButton.setShortcut(QCoreApplication.translate("MainWindow", u"Return", None))
#endif // QT_CONFIG(shortcut)
        self.delPushButton.setText(QCoreApplication.translate("MainWindow", u"\u5220\u9664", None))
#if QT_CONFIG(shortcut)
        self.delPushButton.setShortcut(QCoreApplication.translate("MainWindow", u"Del", None))
#endif // QT_CONFIG(shortcut)
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"\u6587\u4ef6", None))
        self.addFileMenu.setTitle(QCoreApplication.translate("MainWindow", u"\u65b0\u589e\u8bb0\u5f55", None))
    # retranslateUi

