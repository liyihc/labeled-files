# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'file.ui'
##
## Created by: Qt User Interface Compiler version 6.3.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDateTimeEdit, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QMenuBar,
    QPlainTextEdit, QPushButton, QSizePolicy, QStatusBar,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(331, 440)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.idLabel = QLabel(self.centralwidget)
        self.idLabel.setObjectName(u"idLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.idLabel)

        self.idLineEdit = QLineEdit(self.centralwidget)
        self.idLineEdit.setObjectName(u"idLineEdit")
        self.idLineEdit.setEnabled(False)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.idLineEdit)

        self.shownNameLabel = QLabel(self.centralwidget)
        self.shownNameLabel.setObjectName(u"shownNameLabel")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.shownNameLabel)

        self.shownNameLineEdit = QLineEdit(self.centralwidget)
        self.shownNameLineEdit.setObjectName(u"shownNameLineEdit")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.shownNameLineEdit)

        self.pathLabel = QLabel(self.centralwidget)
        self.pathLabel.setObjectName(u"pathLabel")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.pathLabel)

        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_3)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.label)

        self.tagLineEdit = QLineEdit(self.centralwidget)
        self.tagLineEdit.setObjectName(u"tagLineEdit")

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.tagLineEdit)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(7, QFormLayout.LabelRole, self.label_2)

        self.plainTextEdit = QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setObjectName(u"plainTextEdit")

        self.formLayout.setWidget(7, QFormLayout.FieldRole, self.plainTextEdit)

        self.dateTimeEdit = QDateTimeEdit(self.centralwidget)
        self.dateTimeEdit.setObjectName(u"dateTimeEdit")
        self.dateTimeEdit.setCalendarPopup(True)

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.dateTimeEdit)

        self.label_4 = QLabel(self.centralwidget)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.label_4)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.iconLabel = QLabel(self.centralwidget)
        self.iconLabel.setObjectName(u"iconLabel")

        self.horizontalLayout_2.addWidget(self.iconLabel)

        self.iconDefaultPushButton = QPushButton(self.centralwidget)
        self.iconDefaultPushButton.setObjectName(u"iconDefaultPushButton")

        self.horizontalLayout_2.addWidget(self.iconDefaultPushButton)

        self.iconChoosePushButton = QPushButton(self.centralwidget)
        self.iconChoosePushButton.setObjectName(u"iconChoosePushButton")

        self.horizontalLayout_2.addWidget(self.iconChoosePushButton)

        self.iconImageChoosePushButton = QPushButton(self.centralwidget)
        self.iconImageChoosePushButton.setObjectName(u"iconImageChoosePushButton")

        self.horizontalLayout_2.addWidget(self.iconImageChoosePushButton)


        self.formLayout.setLayout(6, QFormLayout.FieldRole, self.horizontalLayout_2)

        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.widget)

        self.actualNameLabel = QLabel(self.centralwidget)
        self.actualNameLabel.setObjectName(u"actualNameLabel")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.actualNameLabel)

        self.actualNameLineEdit = QLineEdit(self.centralwidget)
        self.actualNameLineEdit.setObjectName(u"actualNameLineEdit")
        self.actualNameLineEdit.setEnabled(False)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.actualNameLineEdit)


        self.verticalLayout.addLayout(self.formLayout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.cancelPushButton = QPushButton(self.centralwidget)
        self.cancelPushButton.setObjectName(u"cancelPushButton")

        self.horizontalLayout.addWidget(self.cancelPushButton)

        self.confirmPushButton = QPushButton(self.centralwidget)
        self.confirmPushButton.setObjectName(u"confirmPushButton")

        self.horizontalLayout.addWidget(self.confirmPushButton)


        self.verticalLayout.addLayout(self.horizontalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 331, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.idLabel.setText(QCoreApplication.translate("MainWindow", u"id", None))
        self.shownNameLabel.setText(QCoreApplication.translate("MainWindow", u"\u663e\u793a\u540d", None))
        self.pathLabel.setText(QCoreApplication.translate("MainWindow", u"\u8def\u5f84", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u65f6\u95f4", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u6807\u7b7e", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u63cf\u8ff0", None))
        self.dateTimeEdit.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yy/MM/dd HH:mm:ss", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"\u56fe\u6807", None))
        self.iconLabel.setText(QCoreApplication.translate("MainWindow", u"\u65e0\u56fe\u6807", None))
        self.iconDefaultPushButton.setText(QCoreApplication.translate("MainWindow", u"\u9ed8\u8ba4\u56fe\u6807", None))
        self.iconChoosePushButton.setText(QCoreApplication.translate("MainWindow", u"\u9009\u62e9\u56fe\u6807", None))
        self.iconImageChoosePushButton.setText(QCoreApplication.translate("MainWindow", u"\u9009\u62e9\u56fe\u7247", None))
        self.actualNameLabel.setText(QCoreApplication.translate("MainWindow", u"\u771f\u5b9e\u540d", None))
        self.cancelPushButton.setText(QCoreApplication.translate("MainWindow", u"\u53d6\u6d88", None))
        self.confirmPushButton.setText(QCoreApplication.translate("MainWindow", u"\u786e\u8ba4", None))
#if QT_CONFIG(shortcut)
        self.confirmPushButton.setShortcut(QCoreApplication.translate("MainWindow", u"Return", None))
#endif // QT_CONFIG(shortcut)
    # retranslateUi

