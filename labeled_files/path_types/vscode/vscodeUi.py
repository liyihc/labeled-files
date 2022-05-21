# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'vscode.ui'
##
## Created by: Qt User Interface Compiler version 6.2.2
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QRadioButton, QSizePolicy,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.setEnabled(True)
        Form.resize(400, 300)
        self.formLayout = QFormLayout(Form)
        self.formLayout.setObjectName(u"formLayout")
        self.localRadioButton = QRadioButton(Form)
        self.localRadioButton.setObjectName(u"localRadioButton")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.localRadioButton)

        self.remoteRadioButton = QRadioButton(Form)
        self.remoteRadioButton.setObjectName(u"remoteRadioButton")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.remoteRadioButton)

        self.localLineEdit = QLineEdit(Form)
        self.localLineEdit.setObjectName(u"localLineEdit")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.localLineEdit)

        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label)

        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_2)

        self.remoteHostLineEdit = QLineEdit(Form)
        self.remoteHostLineEdit.setObjectName(u"remoteHostLineEdit")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.remoteHostLineEdit)

        self.remotePathLineEdit = QLineEdit(Form)
        self.remotePathLineEdit.setObjectName(u"remotePathLineEdit")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.remotePathLineEdit)

        self.groupBox = QGroupBox(Form)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout = QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.folderRadioButton = QRadioButton(self.groupBox)
        self.folderRadioButton.setObjectName(u"folderRadioButton")

        self.horizontalLayout.addWidget(self.folderRadioButton)

        self.workspaceRadioButton = QRadioButton(self.groupBox)
        self.workspaceRadioButton.setObjectName(u"workspaceRadioButton")

        self.horizontalLayout.addWidget(self.workspaceRadioButton)

        self.fileRadioButton = QRadioButton(self.groupBox)
        self.fileRadioButton.setObjectName(u"fileRadioButton")

        self.horizontalLayout.addWidget(self.fileRadioButton)


        self.formLayout.setWidget(0, QFormLayout.SpanningRole, self.groupBox)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.localRadioButton.setText(QCoreApplication.translate("Form", u"\u672c\u673a", None))
        self.remoteRadioButton.setText(QCoreApplication.translate("Form", u"\u8fdc\u7a0b", None))
        self.label.setText(QCoreApplication.translate("Form", u"\u4e3b\u673a\u540d", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\u4e3b\u673a\u6587\u4ef6\u7cfb\u7edf", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", u"\u7c7b\u578b", None))
        self.folderRadioButton.setText(QCoreApplication.translate("Form", u"\u6587\u4ef6\u5939", None))
        self.workspaceRadioButton.setText(QCoreApplication.translate("Form", u"\u5de5\u4f5c\u533a", None))
        self.fileRadioButton.setText(QCoreApplication.translate("Form", u"\u5355\u6587\u4ef6", None))
    # retranslateUi

