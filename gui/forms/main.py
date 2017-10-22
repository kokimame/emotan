# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design/main.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(522, 636)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.buttonBox = QtWidgets.QWidget(self.centralwidget)
        self.buttonBox.setStyleSheet("background-color: rgb(200,200,200)")
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.buttonBox)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.addButton = QtWidgets.QPushButton(self.buttonBox)
        self.addButton.setText("")
        self.addButton.setObjectName("addButton")
        self.horizontalLayout.addWidget(self.addButton)
        self.delButton = QtWidgets.QPushButton(self.buttonBox)
        self.delButton.setText("")
        self.delButton.setObjectName("delButton")
        self.horizontalLayout.addWidget(self.delButton)
        self.editButton = QtWidgets.QPushButton(self.buttonBox)
        self.editButton.setText("")
        self.editButton.setObjectName("editButton")
        self.horizontalLayout.addWidget(self.editButton)
        self.dlButton = QtWidgets.QPushButton(self.buttonBox)
        self.dlButton.setText("")
        self.dlButton.setObjectName("dlButton")
        self.horizontalLayout.addWidget(self.dlButton)
        self.transButton = QtWidgets.QPushButton(self.buttonBox)
        self.transButton.setText("")
        self.transButton.setObjectName("transButton")
        self.horizontalLayout.addWidget(self.transButton)
        self.configButton = QtWidgets.QPushButton(self.buttonBox)
        self.configButton.setText("")
        self.configButton.setObjectName("configButton")
        self.horizontalLayout.addWidget(self.configButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.mp3Button = QtWidgets.QPushButton(self.centralwidget)
        self.mp3Button.setObjectName("mp3Button")
        self.horizontalLayout_2.addWidget(self.mp3Button)
        self.pdfButton = QtWidgets.QPushButton(self.centralwidget)
        self.pdfButton.setObjectName("pdfButton")
        self.horizontalLayout_2.addWidget(self.pdfButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 522, 25))
        self.menubar.setNativeMenuBar(False)
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuTools = QtWidgets.QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.actionUndo = QtWidgets.QAction(MainWindow)
        self.actionUndo.setObjectName("actionUndo")
        self.actionImport = QtWidgets.QAction(MainWindow)
        self.actionImport.setObjectName("actionImport")
        self.action_Exit = QtWidgets.QAction(MainWindow)
        self.action_Exit.setObjectName("action_Exit")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionExtract = QtWidgets.QAction(MainWindow)
        self.actionExtract.setObjectName("actionExtract")
        self.actionPreferences = QtWidgets.QAction(MainWindow)
        self.actionPreferences.setObjectName("actionPreferences")
        self.actionWav2Mp3 = QtWidgets.QAction(MainWindow)
        self.actionWav2Mp3.setObjectName("actionWav2Mp3")
        self.actionMp3Volume = QtWidgets.QAction(MainWindow)
        self.actionMp3Volume.setObjectName("actionMp3Volume")
        self.actionNewSfx = QtWidgets.QAction(MainWindow)
        self.actionNewSfx.setEnabled(False)
        self.actionNewSfx.setObjectName("actionNewSfx")
        self.actionRecording = QtWidgets.QAction(MainWindow)
        self.actionRecording.setEnabled(False)
        self.actionRecording.setObjectName("actionRecording")
        self.menuFile.addAction(self.actionExtract)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionPreferences)
        self.menuTools.addAction(self.actionWav2Mp3)
        self.menuTools.addAction(self.actionMp3Volume)
        self.menuTools.addAction(self.actionNewSfx)
        self.menuTools.addAction(self.actionRecording)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Emotan えも単"))
        self.mp3Button.setText(_translate("MainWindow", "Get MP3"))
        self.pdfButton.setText(_translate("MainWindow", "Get PDF"))
        self.menuFile.setTitle(_translate("MainWindow", "&File"))
        self.menuEdit.setTitle(_translate("MainWindow", "&Edit"))
        self.menuTools.setTitle(_translate("MainWindow", "&Tools"))
        self.menuHelp.setTitle(_translate("MainWindow", "&Help"))
        self.actionUndo.setText(_translate("MainWindow", "&Undo"))
        self.actionImport.setText(_translate("MainWindow", "&Import..."))
        self.action_Exit.setText(_translate("MainWindow", "&Exit"))
        self.actionExit.setText(_translate("MainWindow", "&Exit"))
        self.actionExtract.setText(_translate("MainWindow", "Extract..."))
        self.actionPreferences.setText(_translate("MainWindow", "Preferences"))
        self.actionWav2Mp3.setText(_translate("MainWindow", "Convert WAV to MP3"))
        self.actionMp3Volume.setText(_translate("MainWindow", "Change volume of MP3 file"))
        self.actionNewSfx.setText(_translate("MainWindow", "Create new sound effect"))
        self.actionRecording.setText(_translate("MainWindow", "Voice recoder"))

