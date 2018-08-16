import os
import platform
import sys

from PyQt4.QtCore import (PYQT_VERSION_STR, QFile, QFileInfo, QSettings,
                          QString, QT_VERSION_STR, QTimer, QVariant, Qt, QDir, QReadLocker, QReadWriteLock, QRectF)
from PyQt4.QtCore import pyqtSignal as Signal
from PyQt4.QtGui import *
import pyqtgraph as pg  # built on PYQT4 / PySide and numpy
import numpy as np
from Config import Config

import unit
from Components.Material import Material
from Visualisation import MyMessageBox


class NewMatWindow(QMainWindow):
    """
    'New Material' Window launched by the action 'Material' in the menu 'Add' of PyVASCO.
    """
    def __init__(self, parent=None):
        super(NewMatWindow, self).__init__(parent)
        self.tabWidget = QTabWidget()
        self.create_widgets()
        self.setCentralWidget(self.tabWidget)
        self.create_connections()
        self.setWindowTitle("New Material")
        self.initiate_window()

    def create_widgets(self):
        """
       Calls the methods 'create_tab1()' and 'create_tab2()' .
       """
        self.create_tab1()
        self.create_tab2()

    def create_tab1(self):
        """
        Creates and initializes all widgets in tab 1.
        """
        tab1Widget = QWidget()

        Frame1 = QGroupBox("Load Data")
        # widgets for FRAME 1
        infoLabel = QLabel("Select new material from file")

        self.MaterialEdit = QLineEdit()
        self.MaterialButton = QPushButton("Directory")
        self.SaveMaterialButton = QPushButton("Save Material")

        frame1Layout = QGridLayout()  # how the items within one frame are aligned
        frame1Layout.addWidget(infoLabel, 0, 0)
        frame1Layout.addWidget(self.MaterialButton, 1,0)
        frame1Layout.addWidget(self.MaterialEdit, 1,1)
        frame1Layout.addWidget(self.SaveMaterialButton, 2, 1)

        Frame1.setLayout(frame1Layout)

        tab1Layout = QVBoxLayout()
        tab1Layout.addWidget(Frame1)
        tab1Widget.setLayout(tab1Layout)
        self.tabWidget.addTab(tab1Widget, "Data")


    def create_tab2(self):
        """
        Creates and initializes all widgets in tab 2.
        """
        tab2Widget = QWidget()

        Frame2 = QGroupBox("Write New Material")
        self.MaterialNameLabel = QLabel("New Material Name: ")
        self.MaterialNameEdit = QLineEdit("")
        self.table_widget = QTableWidget()


        Frame3 = QGroupBox("Save Material")
        self.SaveMaterialButton2 = QPushButton("Save")
        Frame3.setFixedHeight(75)

        frame2Layout = QGridLayout()
        frame2Layout.addWidget(self.MaterialNameLabel,0,0)
        frame2Layout.addWidget(self.MaterialNameEdit,0,1)
        frame2Layout.addWidget(self.table_widget,1,0,10,2)
        self.populate()

        frame3Layout= QGridLayout()
        frame3Layout.addWidget(self.SaveMaterialButton2)


        tab2Layout = QVBoxLayout()
        Frame2.setLayout(frame2Layout)

        Frame3.setLayout(frame3Layout)
        tab2Layout.addWidget(Frame2)
        tab2Layout.addWidget(Frame3)

        tab2Widget.setLayout(tab2Layout)
        self.tabWidget.addTab(tab2Widget, "Write New Material")

    def initiate_window(self):
        pass

    def populate(self):
        """
        Sets number of rows and columns and corresponding labels in the input table.
        """

        self.table_widget.setRowCount(9)
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels([ 'H2', 'CH4', "CO", 'CO2'])
        self.table_widget.setVerticalHeaderLabels([ "alpha", "eta_ion","","","",'eta_e', 'eta_ph', 'Cbs', 'Qth'])



    def create_connections(self):
        """
        Creates the connections between the GUI widgets and the callback functions.
        """

        print('create_connections')
        #self.unitComboBox.currentIndexChanged.connect(self.unitchange)
        self.MaterialButton.clicked.connect(self.openDirectoryMaterial)
        self.SaveMaterialButton.clicked.connect(self.SaveMaterial)
        self.SaveMaterialButton2.clicked.connect(self.SaveCustomMaterial)

    def openDirectoryMaterial(self):
        """
        Opens the directory containing a new Material .
        """

        dir = (
        os.path.dirname(Config.DataFolder + 'Input/'))  # if self.filename is not None else Config.DataFolder+'Input/')
        fname = unicode(QFileDialog.getOpenFileName(self, "Choose CSV-file to upload data", dir))

        self.MaterialEdit.setText(fname)

    def SaveMaterial(self):
        """
        Copies the file containg the new Material in the corresponding directory, so it will be properly detected by the PyVASCO. In case of error, launches a warning message.
        """

        f = open(self.MaterialEdit.text())
        lines = f.readlines()
        f.close()
        lines = [l.strip("\n").split(",") for l in lines]
        print lines
        if (lines[1][0].lower() != "alpha" or lines[2][0].lower() != "eta_ion" or lines[6][0].lower() != "eta_e" or \
            lines[7][0].lower() != "eta_ph" or lines[8][0] != "Cbs" or lines[9][0] != "Qth" or len(lines[0]) != 4):
            msg = MyMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Wrong format for material! ")
            msg.setInformativeText("This is additional information")
            msg.setWindowTitle("Material Warning Bow")
            msg.setDetailedText("A Material file should be a CSV file with the following structure: \n\n"
                                "| Name of the material | H2|CH4| CO|CO2 \n"
                                "|----------------------|---|---|---|---- \n"
                                "|          alpha       |   |   |   |       \n"
                                "|----------------------|---|---|---|---- \n"
                                "|          eta_ion     |   |   |   |       \n"
                                "|                      |   |   |   |\n"
                                "|                      |   |   |   |\n"
                                "|                      |   |   |   |\n"
                                "|----------------------|---|---|---|---- \n"
                                "|          eta_e       |   |   |   |\n"
                                "|----------------------|---|---|---|---- \n"
                                "|          eta_ph      |   |   |   |\n"
                                "|----------------------|---|---|---|---- \n"
                                "|           Cbs        |   |   |   |\n"
                                "|----------------------|---|---|---|---- \n"
                                "|           Qth        |   |   |   |\n"
                                "|----------------------|---|---|---|---- \n")
            msg.exec_()

        else:
            name = os.path.split(self.MaterialEdit.text())
            if name[0] != Config.MaterialFolder:
                NewMaterial = os.path.join(Config.MaterialFolder, name[1])
                os.rename(name, NewMaterial)
            else:
                NewMaterial = self.MaterialEdit.text()

            NewMaterial = Material(NewMaterial)
            Config.Config.LoadMaterials()

    def SaveCustomMaterial(self):
        """
        Creates a file in the corresponding input folder for the Material defined in the tab 'Write New Material' of the 'New Material' window.
        """

        self.MaterialName = self.MaterialNameEdit.text()
        if not os.path.isfile(Config.MaterialFolder + self.MaterialName + ".csv"):
            f = open(Config.MaterialFolder + self.MaterialName + ".csv", "w")
            f.write(self.MaterialName + ", H2 , CH4, CO, CO2 \n")
            labels = ["alpha", "eta_ion","","","",'eta_e', 'eta_ph', 'Cbs', 'Qth']
            print labels
            for i in range(9):
                cols = ",".join([str(self.table_widget.item(i,j).text()) for j in range(4)]) + "\n"
                f.write(labels[i] + "," + cols)
            f.close()
            Config.LoadMaterials()
        else:
            msg = MyMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("This Material already exists!")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            def msgbtn(i):
                if i.text() == "&Yes":
                    f = open(Config.MaterialFolder + self.MaterialName + ".csv")
                    f.write(self.MaterialName + ", H2 , CH4, CO, CO2 \n")
                    labels = ["alpha", "eta_ion","","","",'eta_e', 'eta_ph', 'Cbs', 'Qth']
                    for i in range(9):
                        cols = ",".join([self.table_widget.item((i, j)).text() for j in range(4)]) + "\n"
                        f.write(labels[i] + "," + cols)
                    f.close()
                    Config.LoadMaterials()
                else:
                    pass

            msg.buttonClicked.connect(msgbtn)











if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = NewMatWindow()
    ex.show()
    app.exec_()


