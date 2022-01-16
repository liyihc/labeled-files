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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QFrame,
    QHBoxLayout, QHeaderView, QLineEdit, QListView,
    QListWidget, QListWidgetItem, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QSpacerItem,
    QStatusBar, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

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

        self.tagLineEdit = QLineEdit(self.centralwidget)
        self.tagLineEdit.setObjectName(u"tagLineEdit")

        self.horizontalLayout.addWidget(self.tagLineEdit)

        self.sortComboBox = QComboBox(self.centralwidget)
        self.sortComboBox.setObjectName(u"sortComboBox")

        self.horizontalLayout.addWidget(self.sortComboBox)

        self.searchPushButton = QPushButton(self.centralwidget)
        self.searchPushButton.setObjectName(u"searchPushButton")

        self.horizontalLayout.addWidget(self.searchPushButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.tagTableWidget = QTableWidget(self.centralwidget)
        if (self.tagTableWidget.columnCount() < 2):
            self.tagTableWidget.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.tagTableWidget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tagTableWidget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.tagTableWidget.setObjectName(u"tagTableWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tagTableWidget.sizePolicy().hasHeightForWidth())
        self.tagTableWidget.setSizePolicy(sizePolicy)
        self.tagTableWidget.setDragEnabled(True)
        self.tagTableWidget.setDragDropMode(QAbstractItemView.DragOnly)
        self.tagTableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tagTableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tagTableWidget.horizontalHeader().setStretchLastSection(True)
        self.tagTableWidget.verticalHeader().setVisible(False)

        self.horizontalLayout_2.addWidget(self.tagTableWidget)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tagListWidget = QListWidget(self.centralwidget)
        self.tagListWidget.setObjectName(u"tagListWidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.tagListWidget.sizePolicy().hasHeightForWidth())
        self.tagListWidget.setSizePolicy(sizePolicy1)
        self.tagListWidget.setMaximumSize(QSize(16777215, 40))
        palette = QPalette()
        brush = QBrush(QColor(0, 0, 0, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
        brush1 = QBrush(QColor(240, 240, 240, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Button, brush1)
        brush2 = QBrush(QColor(255, 255, 255, 255))
        brush2.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Light, brush2)
        brush3 = QBrush(QColor(227, 227, 227, 255))
        brush3.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Midlight, brush3)
        brush4 = QBrush(QColor(160, 160, 160, 255))
        brush4.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Dark, brush4)
        palette.setBrush(QPalette.Active, QPalette.Mid, brush4)
        palette.setBrush(QPalette.Active, QPalette.Text, brush)
        palette.setBrush(QPalette.Active, QPalette.BrightText, brush2)
        palette.setBrush(QPalette.Active, QPalette.ButtonText, brush)
        palette.setBrush(QPalette.Active, QPalette.Base, brush1)
        palette.setBrush(QPalette.Active, QPalette.Window, brush1)
        brush5 = QBrush(QColor(105, 105, 105, 255))
        brush5.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Shadow, brush5)
        brush6 = QBrush(QColor(0, 120, 215, 255))
        brush6.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Highlight, brush6)
        palette.setBrush(QPalette.Active, QPalette.HighlightedText, brush2)
        brush7 = QBrush(QColor(0, 0, 255, 255))
        brush7.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Link, brush7)
        brush8 = QBrush(QColor(255, 0, 255, 255))
        brush8.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.LinkVisited, brush8)
        brush9 = QBrush(QColor(245, 245, 245, 255))
        brush9.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.AlternateBase, brush9)
        palette.setBrush(QPalette.Active, QPalette.NoRole, brush)
        brush10 = QBrush(QColor(255, 255, 220, 255))
        brush10.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.ToolTipBase, brush10)
        palette.setBrush(QPalette.Active, QPalette.ToolTipText, brush)
        brush11 = QBrush(QColor(0, 0, 0, 128))
        brush11.setStyle(Qt.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Active, QPalette.PlaceholderText, brush11)
#endif
        palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Light, brush2)
        palette.setBrush(QPalette.Inactive, QPalette.Midlight, brush3)
        palette.setBrush(QPalette.Inactive, QPalette.Dark, brush4)
        palette.setBrush(QPalette.Inactive, QPalette.Mid, brush4)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush)
        palette.setBrush(QPalette.Inactive, QPalette.BrightText, brush2)
        palette.setBrush(QPalette.Inactive, QPalette.ButtonText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush2)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Shadow, brush5)
        palette.setBrush(QPalette.Inactive, QPalette.Highlight, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.HighlightedText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Link, brush7)
        palette.setBrush(QPalette.Inactive, QPalette.LinkVisited, brush8)
        palette.setBrush(QPalette.Inactive, QPalette.AlternateBase, brush9)
        brush12 = QBrush(QColor(0, 0, 0, 255))
        brush12.setStyle(Qt.NoBrush)
        palette.setBrush(QPalette.Inactive, QPalette.NoRole, brush12)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipBase, brush10)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipText, brush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush11)
#endif
        brush13 = QBrush(QColor(120, 120, 120, 255))
        brush13.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.WindowText, brush13)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Light, brush2)
        brush14 = QBrush(QColor(247, 247, 247, 255))
        brush14.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Midlight, brush14)
        palette.setBrush(QPalette.Disabled, QPalette.Dark, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.Mid, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.Text, brush13)
        palette.setBrush(QPalette.Disabled, QPalette.BrightText, brush2)
        palette.setBrush(QPalette.Disabled, QPalette.ButtonText, brush13)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Shadow, brush)
        palette.setBrush(QPalette.Disabled, QPalette.Highlight, brush6)
        palette.setBrush(QPalette.Disabled, QPalette.HighlightedText, brush2)
        palette.setBrush(QPalette.Disabled, QPalette.Link, brush7)
        palette.setBrush(QPalette.Disabled, QPalette.LinkVisited, brush8)
        palette.setBrush(QPalette.Disabled, QPalette.AlternateBase, brush9)
        brush15 = QBrush(QColor(0, 0, 0, 255))
        brush15.setStyle(Qt.NoBrush)
        palette.setBrush(QPalette.Disabled, QPalette.NoRole, brush15)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipBase, brush10)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipText, brush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush11)
#endif
        self.tagListWidget.setPalette(palette)
        self.tagListWidget.setFocusPolicy(Qt.NoFocus)
        self.tagListWidget.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.tagListWidget.setFrameShape(QFrame.StyledPanel)
        self.tagListWidget.setFrameShadow(QFrame.Sunken)
        self.tagListWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tagListWidget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tagListWidget.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tagListWidget.setFlow(QListView.LeftToRight)
        self.tagListWidget.setWordWrap(True)

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
        self.searchLineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u641c\u7d22\u6587\u5b57", None))
        self.tagLineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u6807\u7b7e", None))
        self.sortComboBox.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u6392\u5e8f\u9879", None))
        self.searchPushButton.setText(QCoreApplication.translate("MainWindow", u"\u641c\u7d22", None))
#if QT_CONFIG(shortcut)
        self.searchPushButton.setShortcut(QCoreApplication.translate("MainWindow", u"Return", None))
#endif // QT_CONFIG(shortcut)
        ___qtablewidgetitem = self.tagTableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"\u6807\u7b7e", None));
        ___qtablewidgetitem1 = self.tagTableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"\u6b21\u6570", None));
        self.delPushButton.setText(QCoreApplication.translate("MainWindow", u"\u5220\u9664", None))
#if QT_CONFIG(shortcut)
        self.delPushButton.setShortcut(QCoreApplication.translate("MainWindow", u"Del", None))
#endif // QT_CONFIG(shortcut)
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"\u6587\u4ef6", None))
    # retranslateUi

