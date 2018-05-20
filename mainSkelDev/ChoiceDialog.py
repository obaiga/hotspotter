# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ChoiceDialog.ui'
#
# Created: Thu May 10 16:02:53 2018
#      by: PyQt4 UI code generator 4.10
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
        FlankSorting.resize(869, 533)
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
        self.number_prompt = QtGui.QLabel(FlankSorting)
        self.number_prompt.setObjectName(_fromUtf8("number_prompt"))
        self.verticalLayout.addWidget(self.number_prompt)
        self.choice_cats_1 = QtGui.QRadioButton(FlankSorting)
        self.choice_cats_1.setChecked(True)
        self.choice_cats_1.setAutoRepeat(True)
        self.choice_cats_1.setObjectName(_fromUtf8("choice_cats_1"))
        self.verticalLayout.addWidget(self.choice_cats_1)
        self.choice_cats_2 = QtGui.QRadioButton(FlankSorting)
        self.choice_cats_2.setObjectName(_fromUtf8("choice_cats_2"))
        self.verticalLayout.addWidget(self.choice_cats_2)
        self.choice_cats_3 = QtGui.QRadioButton(FlankSorting)
        self.choice_cats_3.setObjectName(_fromUtf8("choice_cats_3"))
        self.verticalLayout.addWidget(self.choice_cats_3)
        self.choice_cats_4 = QtGui.QRadioButton(FlankSorting)
        self.choice_cats_4.setObjectName(_fromUtf8("choice_cats_4"))
        self.verticalLayout.addWidget(self.choice_cats_4)
        self.choice_cats_5more = QtGui.QRadioButton(FlankSorting)
        self.choice_cats_5more.setObjectName(_fromUtf8("choice_cats_5more"))
        self.verticalLayout.addWidget(self.choice_cats_5more)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.flank_promt = QtGui.QLabel(FlankSorting)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.flank_promt.setFont(font)
        self.flank_promt.setObjectName(_fromUtf8("flank_promt"))
        self.verticalLayout.addWidget(self.flank_promt)
        self.left_checker = QtGui.QCheckBox(FlankSorting)
        self.left_checker.setObjectName(_fromUtf8("left_checker"))
        self.verticalLayout.addWidget(self.left_checker)
        self.right_checker = QtGui.QCheckBox(FlankSorting)
        self.right_checker.setObjectName(_fromUtf8("right_checker"))
        self.verticalLayout.addWidget(self.right_checker)
        self.front_checker = QtGui.QCheckBox(FlankSorting)
        self.front_checker.setObjectName(_fromUtf8("front_checker"))
        self.verticalLayout.addWidget(self.front_checker)
        self.back_checker = QtGui.QCheckBox(FlankSorting)
        self.back_checker.setObjectName(_fromUtf8("back_checker"))
        self.verticalLayout.addWidget(self.back_checker)
        self.unknown_checker = QtGui.QCheckBox(FlankSorting)
        self.unknown_checker.setObjectName(_fromUtf8("unknown_checker"))
        self.verticalLayout.addWidget(self.unknown_checker)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.next_button = QtGui.QPushButton(FlankSorting)
        self.next_button.setObjectName(_fromUtf8("next_button"))
        self.verticalLayout.addWidget(self.next_button)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 2, 1, 1)
        self.vertical_line = QtGui.QFrame(FlankSorting)
        self.vertical_line.setFrameShape(QtGui.QFrame.VLine)
        self.vertical_line.setFrameShadow(QtGui.QFrame.Sunken)
        self.vertical_line.setObjectName(_fromUtf8("vertical_line"))
        self.gridLayout.addWidget(self.vertical_line, 0, 1, 1, 1)
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
        self.image_viewer.setPixmap(QtGui.QPixmap(_fromUtf8("../hstest/testdb/test_imgs/02__Station12__Camera2__2012-5-4__22-22-36(6).JPG")))
        self.image_viewer.setScaledContents(True)
        self.image_viewer.setWordWrap(False)
        self.image_viewer.setObjectName(_fromUtf8("image_viewer"))
        self.gridLayout.addWidget(self.image_viewer, 0, 0, 1, 1)

        self.retranslateUi(FlankSorting)
        QtCore.QMetaObject.connectSlotsByName(FlankSorting)

    def retranslateUi(self, FlankSorting):
        FlankSorting.setWindowTitle(_translate("FlankSorting", "HotSpotter - Sorting by Flank...", None))
        self.number_prompt.setText(_translate("FlankSorting", "<html><head/><body><p align=\"center\"><span style=\" font-size:11pt; font-weight:600;\">Number of cats in this image:</span></p></body></html>", None))
        self.choice_cats_1.setText(_translate("FlankSorting", "1", None))
        self.choice_cats_2.setText(_translate("FlankSorting", "2", None))
        self.choice_cats_3.setText(_translate("FlankSorting", "3", None))
        self.choice_cats_4.setText(_translate("FlankSorting", "4", None))
        self.choice_cats_5more.setText(_translate("FlankSorting", "5+", None))
        self.flank_promt.setText(_translate("FlankSorting", "<html><head/><body><p align=\"center\">Indicate the flank(s) of the</p><p align=\"center\">snow leopard:</p></body></html>", None))
        self.left_checker.setText(_translate("FlankSorting", "Left", None))
        self.right_checker.setText(_translate("FlankSorting", "Right", None))
        self.front_checker.setText(_translate("FlankSorting", "Front", None))
        self.back_checker.setText(_translate("FlankSorting", "Back", None))
        self.unknown_checker.setText(_translate("FlankSorting", "Unknown", None))
        self.next_button.setText(_translate("FlankSorting", "Next", None))

