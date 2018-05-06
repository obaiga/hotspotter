# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ChoiceDialog.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_FlankSorting(object):
    def setupUi(self, FlankSorting):
        FlankSorting.setObjectName(_fromUtf8("FlankSorting"))
        FlankSorting.resize(869, 519)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(FlankSorting.sizePolicy().hasHeightForWidth())
        FlankSorting.setSizePolicy(sizePolicy)
        FlankSorting.setMaximumSize(QtCore.QSize(2277, 1560))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("hsicon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        FlankSorting.setWindowIcon(icon)
        FlankSorting.setAutoFillBackground(True)
        self.gridLayout = QtGui.QGridLayout(FlankSorting)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.label_2 = QtGui.QLabel(FlankSorting)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.radioButton = QtGui.QRadioButton(FlankSorting)
        self.radioButton.setChecked(True)
        self.radioButton.setAutoRepeat(True)
        self.radioButton.setObjectName(_fromUtf8("radioButton"))
        self.verticalLayout.addWidget(self.radioButton)
        self.radioButton_2 = QtGui.QRadioButton(FlankSorting)
        self.radioButton_2.setObjectName(_fromUtf8("radioButton_2"))
        self.verticalLayout.addWidget(self.radioButton_2)
        self.radioButton_3 = QtGui.QRadioButton(FlankSorting)
        self.radioButton_3.setObjectName(_fromUtf8("radioButton_3"))
        self.verticalLayout.addWidget(self.radioButton_3)
        self.radioButton_4 = QtGui.QRadioButton(FlankSorting)
        self.radioButton_4.setObjectName(_fromUtf8("radioButton_4"))
        self.verticalLayout.addWidget(self.radioButton_4)
        self.radioButton_5 = QtGui.QRadioButton(FlankSorting)
        self.radioButton_5.setObjectName(_fromUtf8("radioButton_5"))
        self.verticalLayout.addWidget(self.radioButton_5)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.label = QtGui.QLabel(FlankSorting)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.checkBox = QtGui.QCheckBox(FlankSorting)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.verticalLayout.addWidget(self.checkBox)
        self.checkBox_4 = QtGui.QCheckBox(FlankSorting)
        self.checkBox_4.setObjectName(_fromUtf8("checkBox_4"))
        self.verticalLayout.addWidget(self.checkBox_4)
        self.checkBox_3 = QtGui.QCheckBox(FlankSorting)
        self.checkBox_3.setObjectName(_fromUtf8("checkBox_3"))
        self.verticalLayout.addWidget(self.checkBox_3)
        self.checkBox_2 = QtGui.QCheckBox(FlankSorting)
        self.checkBox_2.setObjectName(_fromUtf8("checkBox_2"))
        self.verticalLayout.addWidget(self.checkBox_2)
        self.checkBox_5 = QtGui.QCheckBox(FlankSorting)
        self.checkBox_5.setObjectName(_fromUtf8("checkBox_5"))
        self.verticalLayout.addWidget(self.checkBox_5)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.next_btn = QtGui.QPushButton(FlankSorting)
        self.next_btn.setObjectName(_fromUtf8("next_btn"))
        self.verticalLayout.addWidget(self.next_btn)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 2, 1, 1)
        self.line_2 = QtGui.QFrame(FlankSorting)
        self.line_2.setFrameShape(QtGui.QFrame.VLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.gridLayout.addWidget(self.line_2, 0, 1, 1, 1)
        self.image_viewer = QtGui.QLabel(FlankSorting)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.image_viewer.sizePolicy().hasHeightForWidth())
        self.image_viewer.setSizePolicy(sizePolicy)
        self.image_viewer.setMaximumSize(QtCore.QSize(640, 480))
        font = QtGui.QFont()
        font.setKerning(True)
        self.image_viewer.setFont(font)
        self.image_viewer.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.image_viewer.setAutoFillBackground(False)
        self.image_viewer.setFrameShadow(QtGui.QFrame.Plain)
        self.image_viewer.setText(_fromUtf8(""))
        self.image_viewer.setPixmap(QtGui.QPixmap(_fromUtf8("../../Google Drive/gitCode/code/hotspotter/hstest/testdb/timtest/images/02__Station12__Camera2__2012-5-4__22-22-36(7).JPG")))
        self.image_viewer.setScaledContents(True)
        self.image_viewer.setWordWrap(False)
        self.image_viewer.setObjectName(_fromUtf8("image_viewer"))
        self.gridLayout.addWidget(self.image_viewer, 0, 0, 1, 1)

        self.retranslateUi(FlankSorting)
        QtCore.QMetaObject.connectSlotsByName(FlankSorting)

    def retranslateUi(self, FlankSorting):
        FlankSorting.setWindowTitle(_translate("FlankSorting", "HotSpotter - Sorting by Flank...", None))
        self.label_2.setText(_translate("FlankSorting", "<html><head/><body><p align=\"center\"><span style=\" font-size:11pt; font-weight:600;\">Number of cats in this image:</span></p></body></html>", None))
        self.radioButton.setText(_translate("FlankSorting", "1", None))
        self.radioButton_2.setText(_translate("FlankSorting", "2", None))
        self.radioButton_3.setText(_translate("FlankSorting", "3", None))
        self.radioButton_4.setText(_translate("FlankSorting", "4", None))
        self.radioButton_5.setText(_translate("FlankSorting", "5+", None))
        self.label.setText(_translate("FlankSorting", "<html><head/><body><p align=\"center\">Indicate the flank(s) of the</p><p align=\"center\">snow leopard:</p></body></html>", None))
        self.checkBox.setText(_translate("FlankSorting", "Left", None))
        self.checkBox_4.setText(_translate("FlankSorting", "Right", None))
        self.checkBox_3.setText(_translate("FlankSorting", "Front", None))
        self.checkBox_2.setText(_translate("FlankSorting", "Back", None))
        self.checkBox_5.setText(_translate("FlankSorting", "Unknown", None))
        self.next_btn.setText(_translate("FlankSorting", "Next", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    FlankSorting = QtGui.QDialog()
    ui = Ui_FlankSorting()
    ui.setupUi(FlankSorting)
    FlankSorting.show()
    sys.exit(app.exec_())

