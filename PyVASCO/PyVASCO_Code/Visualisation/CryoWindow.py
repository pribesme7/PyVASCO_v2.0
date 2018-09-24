# -*- coding: utf8 -*-
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

#import unit
#from Components.Material import Material
from __init__ import MyMessageBox,ReadComponent,ReWrite


class CryoWindow(QMainWindow):
    """
    'Cryogenics' Window launched by the action 'Cryogenics' in the menu 'Add and Edit' of PyVASCO.
    """
    def __init__(self, parent=None):
        super(CryoWindow, self).__init__(parent)
        self.tabWidget = QTabWidget()
        self.create_widgets()
        self.setCentralWidget(self.tabWidget)
        self.create_connections()
        self.setWindowTitle("Cryogenics")
        #self.initiate_window()

    def create_widgets(self):
        """
       Calls the methods 'create_tab1()' and 'create_tab2()' .
       """

        #self.create_tab1()
        self.create_tab2()


    def create_tab1(self):
        """
        Creates and initializes all widgets in tab 1.
        """
        tab1Widget = QWidget()

        Frame1 = QGroupBox("Select material")
        # widgets for FRAME 1
        infoLabel = QLabel("Select material from file")

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
        self.tabWidget.addTab(tab1Widget, "Select material")


    def create_tab2(self):
        """
        Creates and initializes all widgets in tab 2.
        """
        tab2Widget = QWidget()
        tab2Layout = QGridLayout()

        # Widgets for Frame 0
        Frame0 = QGroupBox("Select material")
        self.MaterialPushButton = QPushButton("Select material")
        self.MaterialEdit = QLineEdit("")

        # Wodgets fpr Frame 1

        Frame1 =  QGroupBox("H2")

        self.H2CryoTable = QTableWidget()
        self.H2CryoTable.setRowCount(2)
        self.H2CryoTable.setColumnCount(20)
        self.H2CryoTable.setVerticalHeaderLabels(["T [K]", "Sticking"])


        # Wodgets fpr Frame 2

        Frame2 = QGroupBox("CH4")
        self.CH4CryoTable = QTableWidget()
        self.CH4CryoTable.setRowCount(2)
        self.CH4CryoTable.setColumnCount(20)
        self.CH4CryoTable.setVerticalHeaderLabels(["T [K]", "Sticking"])

        # Wodgets fpr Frame 3

        Frame3 = QGroupBox("CO")
        self.COCryoTable = QTableWidget()
        self.COCryoTable.setRowCount(2)
        self.COCryoTable.setColumnCount(20)
        self.COCryoTable.setVerticalHeaderLabels(["T [K]", "Sticking"])

        # Wodgets fpr Frame 4

        Frame4 = QGroupBox("CO2")
        self.CO2CryoTable = QTableWidget()
        self.CO2CryoTable.setRowCount(2)
        self.CO2CryoTable.setColumnCount(20)
        self.CO2CryoTable.setVerticalHeaderLabels(["T [K]", "Sticking"])

        # Widgets for Frame 5
        Frame5 = QGroupBox("")
        self.SavePushButton = QPushButton("Save")


        #Layout Frame 0
        frame0Layout = QGridLayout()
        frame0Layout.addWidget(self.MaterialPushButton,0,0)
        frame0Layout.addWidget(self.MaterialEdit,0,1)
        Frame0.setLayout(frame0Layout)
        tab2Layout.addWidget(Frame0,0,0,1,2)

        # Layout Frame 1 
        frame1Layout = QGridLayout()

        frame1Layout.addWidget(self.H2CryoTable,0,0,2,2)
        Frame1.setLayout(frame1Layout)
        tab2Layout.addWidget(Frame1,1,0)

        # Layout Frame 2 
        frame2Layout = QGridLayout()

        frame2Layout.addWidget(self.CH4CryoTable, 0, 0, 2, 2)
        Frame2.setLayout(frame2Layout)
        tab2Layout.addWidget(Frame2, 1, 1)

        # Layout Frame 3  
        frame3Layout = QGridLayout()

        frame3Layout.addWidget(self.COCryoTable, 0, 0, 2, 2)
        Frame3.setLayout(frame3Layout)
        tab2Layout.addWidget(Frame3, 2, 0)

        # Layout Frame 4 
        frame4Layout = QGridLayout()

        frame4Layout.addWidget(self.CO2CryoTable, 0, 0, 2, 2)
        Frame4.setLayout(frame4Layout)
        tab2Layout.addWidget(Frame4, 2, 1)

        # Layout Frame 5
        frame5Layout = QGridLayout()
        frame5Layout.addWidget(self.SavePushButton,0,0)
        Frame5.setLayout(frame5Layout)
        tab2Layout.addWidget(Frame5,3,0,1,2)

        tab2Widget.setLayout(tab2Layout)

        self.tabWidget.addTab(tab2Widget, "Custom cryogenic behavior")

    def create_connections(self):
        """
        Creates the connections between the GUI widgets and the callback functions.

        """
        self.MaterialPushButton.clicked.connect(self.LoadMaterial)
        self.SavePushButton.clicked.connect(self.SaveCryogenicsSetup)

    def LoadMaterial(self):
        """
        Opens the directory containing a new Material .
        """

        dir = Config.MaterialFolder
        fname = unicode(QFileDialog.getOpenFileName(self, "Choose CSV-file to upload data", dir))

        self.MaterialEdit.setText(fname)

    def SaveCryogenicsSetup(self):
        """
        Saves the cryogenic setup for the choosen material

        """
        Material = os.path.split(str(self.MaterialEdit.text()))[-1]
        
        # H2 data
        H2Sticking = [[],[]]
        
        for j in range(self.H2CryoTable.columnCount()):
                try:
                    H2Sticking[0].append(str(self.H2CryoTable.item(0,j).text()))
                    H2Sticking[1].append(str(self.H2CryoTable.item(1, j).text()))
                except:
                    H2Sticking[0].append("")
                    H2Sticking[1].append("")

        H2Sticking[0] =  filter(None,H2Sticking[0])
        H2Sticking[1] = filter(None, H2Sticking[1])


        CH4Sticking = [[], []]

        for j in range(self.CH4CryoTable.columnCount()):
            try:
                CH4Sticking[0].append(str(self.CH4CryoTable.item(0, j).text()))
                CH4Sticking[1].append(str(self.CH4CryoTable.item(1, j).text()))
            except:
                CH4Sticking[0].append("")
                CH4Sticking[0].append("")
                
        CH4Sticking[0] = filter(None,CH4Sticking[0])
        CH4Sticking[1] = filter(None, CH4Sticking[1])
        

        COSticking = [[], []]

        for j in range(self.COCryoTable.columnCount()):
            try:
                COSticking[0].append(str(self.COCryoTable.item(0, j).text()))
                COSticking[1].append(str(self.COCryoTable.item(1, j).text()))
            except:
                COSticking[0].append("")
                COSticking[1].append("")

        COSticking[0] = filter(None, COSticking[0])
        COSticking[1] = filter(None, COSticking[1])

        # CO2 data

        CO2Sticking = [[], []]

        for j in range(self.CO2CryoTable.columnCount()):
            try:
                CO2Sticking[0].append(str(self.CO2CryoTable.item(0, j).text()))
                CO2Sticking[1].append(str(self.CO2CryoTable.item(1, j).text()))
            except:
                CO2Sticking[0].append("")
                CO2Sticking[1].append("")

        CO2Sticking[0] = filter(None, CO2Sticking[0])
        CO2Sticking[1] = filter(None, CO2Sticking[1])


        
        f = open(Config.CryogenicsFolder + Material, "w" )
        # H2 
        f.write("T [K]," + ",".join(H2Sticking[0]) + "\n")
        f.write("alpha'H2," + ",".join(H2Sticking[1]) + "\n")

        # CH4 
        f.write("T [K]," + ",".join(CH4Sticking[0]) + "\n")
        f.write("alpha'CH4," + ",".join(CH4Sticking[1]) + "\n")

        # CO 
        f.write("T [K]," + ",".join(COSticking[0]) + "\n")
        f.write("alpha'CO," + ",".join(COSticking[1]) + "\n")

        # CO2 
        f.write("T [K]," + ",".join(CO2Sticking[0]) + "\n")
        f.write("alpha'CO2," + ",".join(CO2Sticking[1]) + "\n")
        
        f.close()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = CryoWindow()
    ex.show()
    app.exec_()

