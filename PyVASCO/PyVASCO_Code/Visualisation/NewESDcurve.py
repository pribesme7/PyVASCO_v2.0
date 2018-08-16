import os
import platform
import sys
from shutil import copyfile
from PyQt4.QtCore import (PYQT_VERSION_STR, QFile, QFileInfo, QSettings,
                          QString, QT_VERSION_STR, QTimer, QVariant, Qt, QDir, QReadLocker, QReadWriteLock, QRectF)
from PyQt4.QtCore import pyqtSignal as Signal
from PyQt4.QtGui import *
import pyqtgraph as pg  # built on PYQT4 / PySide and numpy
import numpy as np
from Config import Config
from Visualisation import MyMessageBox

import unit
from Components import ESD, Material


class NewESDWindow(QMainWindow):
    """
    'New ESD curve' Window launched by the action 'ESD curve' in the menu 'Add' of PyVASCO.
    """
    def __init__(self, parent=None):
        super(NewESDWindow, self).__init__(parent)
        self.tabWidget = QTabWidget()
        self.create_widgets()
        self.setCentralWidget(self.tabWidget)
        self.create_connections()
        self.setWindowTitle("New ESD curve")


    def create_widgets(self):
        """
        Calls the method 'create_tab1()'.
        """
        self.create_tab1()

    def create_tab1(self):
        """
        Creates and initializes all widgets in tab 1.
        """
        tab1Widget = QWidget()

        Frame1 = QGroupBox("Load Data")
        # widgets for FRAME 1

        infoLabelMaterial = QLabel("Select Material from file")
        self.ESDMaterialEdit = QLineEdit()
        self.ESDMaterialButton = QPushButton("Load")

        infoLabel = QLabel("Select the Material ESD curve from file")
        self.ESDCurveEdit = QLineEdit()
        self.ESDCurveButton = QPushButton("Load")

        self.SaveESDCurveButton = QPushButton("Save ESD curve")

        frame1Layout = QGridLayout()  # how the items within one frame are aligned

        frame1Layout.addWidget(infoLabelMaterial, 0, 0)
        frame1Layout.addWidget(self.ESDMaterialEdit,1,0 )
        frame1Layout.addWidget(self.ESDMaterialButton,1,1)
        frame1Layout.addWidget(infoLabel, 2, 0)
        frame1Layout.addWidget(self.ESDCurveEdit, 3,0)
        frame1Layout.addWidget(self.ESDCurveButton, 3, 1)
        frame1Layout.addWidget(self.SaveESDCurveButton,4,0,1,2)

        Frame1.setLayout(frame1Layout)

        tab1Layout = QVBoxLayout()
        tab1Layout.addWidget(Frame1)
        tab1Widget.setLayout(tab1Layout)
        self.tabWidget.addTab(tab1Widget, "Data")

    def create_connections(self):
        """
        Creates the connections between the GUI widgets and the callback functions.
        """
        print('create_connections')
        #self.unitComboBox.currentIndexChanged.connect(self.unitchange)
        self.ESDMaterialButton.clicked.connect(self.openDirectoryMaterial)
        self.ESDCurveButton.clicked.connect(self.openDirectoryESDCurve)
        self.SaveESDCurveButton.clicked.connect(self.SaveESDCurve)


    def openDirectoryESDCurve(self):
        """
        Opens the directory containing the ESD of the selected material.
        """
        dir = (
        os.path.dirname(Config.DataFolder + 'Input/'))  # if self.filename is not None else Config.DataFolder+'Input/')
        fname = unicode(QFileDialog.getOpenFileName(self, "Choose CSV-file to upload data", dir))

        self.ESDCurveEdit.setText(fname)

    def SaveESDCurve(self):
        """
        Copies the file containg the ESD curve for the given material in corresponding directory, so it will be properly detected by the program.
        """
        M = Material.Material(str(self.ESDMaterialEdit.text()))
        MName = M.Name
        copyfile(self.ESDCurveEdit.text(),Config.ESDFolder +"ESD_" + MName + ".csv" )
        Config.LoadMaterials()

    def openDirectoryMaterial(self):
        """
        Opens the directory containing a Material.
        """
        dir = (
        os.path.dirname(Config.DataFolder + 'Input/'))  # if self.filename is not None else Config.DataFolder+'Input/')
        fname = unicode(QFileDialog.getOpenFileName(self, "Choose CSV-file to upload data", dir))

        self.ESDMaterialEdit.setText(fname)







if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = NewESDWindow()
    ex.show()
    app.exec_()


