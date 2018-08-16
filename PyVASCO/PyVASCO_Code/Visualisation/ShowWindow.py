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
from Components import Material,Gassource,Pump
from Visualisation import MyMessageBox


def ReadComponent(File):
    Data = []
    if os.path.isdir(File):
        Name = os.path.split(File)[-1]
        files = os.listdir(File)
        Data = {}
        for f in files:
            p = f.split("_")[-1].split(".")[0]
            data = ReadComponent(File + "/" +  f)
            Data[p] = data
        return Data

    else:

        with open(File,"r") as f:
            lines = f.readlines()

        for l in lines:
            l = l.strip("\n").split(",")
            Data.append(l)

        return [x[1:] for x in Data[1:]]


class ShowWindow(QMainWindow):
    """
    'New Material' Window launched by the action 'Material' in the menu 'Add' of PyVASCO.
    """
    def __init__(self, parent=None):
        super(ShowWindow, self).__init__(parent)
        self.tabWidget = QTabWidget()
        self.create_widgets()
        self.setCentralWidget(self.tabWidget)
        self.create_connections()
        self.setWindowTitle("Show registered components")
        #self.initiate_window()


    def create_widgets(self):
        """
       Calls the methods 'create_tab1()' and 'create_tab2()' .
       """
        self.create_tab1()
        self.create_tab2()
        self.create_tab3()

    def create_tab1(self):
        # Show registered Materials
        tab1Widget = QWidget()
        tab1Layout = QGridLayout()

        Frame2 = QGroupBox("Material")

        self.MaterialNameLabel = QLabel("Name: ")
        self.MaterialNameEdit = QLabel("")
        self.MaterialTableWidget =  QTableWidget()

        self.MaterialTableWidget.setRowCount(9)
        self.MaterialTableWidget.setColumnCount(4)
        self.MaterialTableWidget.setHorizontalHeaderLabels(['H2', 'CH4', "CO", 'CO2'])
        if unit.unit == 0.750062:
            self.MaterialTableWidget.setVerticalHeaderLabels(["alpha", "eta_ion", "", "", "", 'eta_e', 'eta_ph', 'Cbs [l/m/s]', 'Qth [mbar*l/cm^2/s]'])
        elif unit.unit == 1.33322:
            self.MaterialTableWidget.setVerticalHeaderLabels(
                ["alpha", "eta_ion", "", "", "", 'eta_e', 'eta_ph', 'Cbs [l/m/s]', 'Qth [torr*l/cm^2/s]'])

        frame2Layout = QGridLayout()
        frame2Layout.addWidget(self.MaterialNameLabel,0,0,1,1)
        frame2Layout.addWidget(self.MaterialNameEdit, 0, 1,1,1)
        frame2Layout.addWidget(self.MaterialTableWidget,1,0,9,4)
        Frame2.setLayout(frame2Layout)
        Frame2.setMinimumWidth(550)
        Frame2.setMinimumHeight(400)

        Frame1 = QGroupBox("List of Materials")
        self.MaterialsList = self.CreateList(Config.MaterialFolder)
        frame1Layout = QGridLayout()
        frame1Layout.addWidget(self.MaterialsList)
        Frame1.setLayout(frame1Layout)
        Frame1.setFixedWidth(300)

        tab1Layout.addWidget(Frame1,0,0)
        tab1Layout.addWidget(Frame2,0,1)

        tab1Widget.setLayout(tab1Layout)
        self.tabWidget.addTab(tab1Widget, "Materials")


    def create_tab2(self):
        # Show registered Pumps
        tab1Widget = QWidget()
        tab1Layout = QGridLayout()

        Frame2 = QGroupBox("Pump")

        self.PumpNameLabel = QLabel("Name: ")
        self.PumpNameEdit = QLabel("")
        self.PumpTableWidget = QTableWidget()
        self.PumpTableWidget.setRowCount(4)
        self.PumpTableWidget.setColumnCount(1)
        self.PumpTableWidget.setVerticalHeaderLabels(["S_H2 [l/s]", "S_CH4 [l/s]", "S_CO [l/s]", "S_CO2 [l/s]"])
        self.PumpTableWidget.setHorizontalHeaderLabels(["Nominal"])
        frame2Layout = QGridLayout()
        frame2Layout.addWidget(self.PumpNameLabel, 0, 0, 1, 1)
        frame2Layout.addWidget(self.PumpNameEdit, 0, 1, 1, 1)
        frame2Layout.addWidget(self.PumpTableWidget, 1, 0, 9, 4)
        Frame2.setLayout(frame2Layout)
        Frame2.setMinimumWidth(500)
        Frame2.setMinimumHeight(400)

        Frame1 = QGroupBox("List of Pumps")
        self.PumpsList = self.CreateList(Config.PumpFolder)
        frame1Layout = QGridLayout()
        frame1Layout.addWidget(self.PumpsList)
        Frame1.setLayout(frame1Layout)
        Frame1.setFixedWidth(300)

        tab1Layout.addWidget(Frame1, 0, 0)
        tab1Layout.addWidget(Frame2, 0, 1)

        tab1Widget.setLayout(tab1Layout)
        self.tabWidget.addTab(tab1Widget, "Pumps")


    def create_tab3(self):
        # Show registered Materials
        tab1Widget = QWidget()
        tab1Layout = QGridLayout()

        Frame2 = QGroupBox("Gas source")

        self.GasSourceNameLabel = QLabel("Name: ")
        self.GasSourceNameEdit = QLabel("")
        self.GasSourceTableWidget = QTableWidget()
        self.GasSourceTableWidget .setRowCount(4)
        self.GasSourceTableWidget .setColumnCount(1)
        if unit.unit ==  0.750062:
            self.GasSourceTableWidget .setVerticalHeaderLabels(["g_H2 [mbar *l/s]", "g_CH4 [mbar *l/s]", "g_CO [mbar *l/s]",
                                                   "g_CO2 [mbar *l/s]"])
        elif unit.unit ==  1.33322:
            self.GasSourceTableWidget.setVerticalHeaderLabels(
                ["g_H2 [torr *l/s]", "g_CH4 [torr *l/s]", "g_CO [torr *l/s]",
                 "g_CO2 [torr *l/s]"])


        frame2Layout = QGridLayout()
        frame2Layout.addWidget(self.GasSourceNameLabel, 0, 0, 1, 1)
        frame2Layout.addWidget(self.GasSourceNameEdit, 0, 1, 1, 1)
        frame2Layout.addWidget(self.GasSourceTableWidget, 1, 0, 9, 4)
        Frame2.setLayout(frame2Layout)
        Frame2.setMinimumWidth(500)
        Frame2.setMinimumHeight(400)

        Frame1 = QGroupBox("List of Gas sources")
        self.GasSourceList = self.CreateList(Config.GassourceFolder)
        frame1Layout = QGridLayout()
        frame1Layout.addWidget(self.GasSourceList)
        Frame1.setLayout(frame1Layout)
        Frame1.setFixedWidth(300)

        tab1Layout.addWidget(Frame1, 0, 0)
        tab1Layout.addWidget(Frame2, 0, 1)

        tab1Widget.setLayout(tab1Layout)
        self.tabWidget.addTab(tab1Widget, "Gas sources")


    def CreateList(self,Dir):

        listWidget = QListWidget()
        listWidget.resize(300, 120)

        for c in os.listdir(Dir):
            item = ".".join(c.split(".")[:-1])
            if item == "" and os.path.isdir(Dir + "/" + c):
                item = c
            list_item = QListWidgetItem(item,parent=listWidget)

        return listWidget

    def create_connections(self):
        self.MaterialsList.itemClicked.connect(lambda : self.populateTable("Material"))
        self.PumpsList.itemClicked.connect(lambda : self.populateTable("Pump"))
        self.GasSourceList.itemClicked.connect(lambda : self.populateTable("Gas source"))

    def printItem(self):
        item = self.MaterialsList.currentItem().text()
        print item

    def populateTable(self, target):

        if target == "Material":
            item = self.MaterialsList.currentItem().text()
            self.MaterialNameEdit.setText(item)
            Data = ReadComponent(Config.MaterialFolder + item + ".csv")
            for i in range( self.MaterialTableWidget.rowCount()):
                for j in range( self.MaterialTableWidget.columnCount()):
                    self.MaterialTableWidget.setItem(i, j, QTableWidgetItem(str(Data[i][j])))
            self.MaterialTableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        elif target== "Pump":
            item = self.PumpsList.currentItem().text()
            if os.path.isfile(Config.PumpFolder + item + ".csv"):
                self.PumpTableWidget.setColumnCount(1)
                self.PumpTableWidget.setHorizontalHeaderLabels(["Nominal"])
                Data = ReadComponent(Config.PumpFolder + item + ".csv")
                self.PumpNameEdit.setText(item)
                for i in range(self.PumpTableWidget.rowCount()):
                    for j in range(self.PumpTableWidget.columnCount()):
                        self.PumpTableWidget.setItem(i, j, QTableWidgetItem(str(Data[i][j])))

            else:
                Data = ReadComponent(str(Config.PumpFolder + item))
                self.PumpNameEdit.setText(item)
                keys = ["Nominal"] + [k for k in Data.keys() if k != "Nominal"]
                labels = ["Nominal"] + [k + " mbar" for k in Data.keys() if k != "Nominal"]
                self.PumpTableWidget.setColumnCount(len(keys))
                self.PumpTableWidget.setHorizontalHeaderLabels(labels)
                for j, k in enumerate(keys):
                    for i in range(4):
                        self.PumpTableWidget.setItem(i, j, QTableWidgetItem(str(Data[k][i][0])))
            self.PumpTableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)


        elif target == "Gas source":
            item = self.GasSourceList.currentItem().text()
            Data = ReadComponent(Config.GassourceFolder + item + ".csv")
            self.GasSourceNameEdit.setText(item)
            for i in range(self.GasSourceTableWidget.rowCount()):
                for j in range(self.GasSourceTableWidget.columnCount()):
                    self.GasSourceTableWidget.setItem(i, j, QTableWidgetItem(str(Data[i][j])))


#class myListWidget(QListWidget):
#    def Clicked(self,item):
#        print item
#        return item








if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ShowWindow()
    ex.show()
    app.exec_()

