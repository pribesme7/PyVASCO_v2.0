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
from __init__ import MyMessageBox,ReadComponent,ReWrite


class NewMatWindow(QMainWindow):
    """
    'New Material' Window launched by the action 'Material' in the menu 'Add and Edit' of PyVASCO.
    """
    def __init__(self, parent=None):
        super(NewMatWindow, self).__init__(parent)
        self.tabWidget = QTabWidget()
        self.create_widgets()
        self.setCentralWidget(self.tabWidget)
        self.create_connections()
        self.setWindowTitle("New Material")


    def create_widgets(self):
        """
       Calls the methods 'create_tab3()' and 'create_tab2()' .
       """

        self.create_tab3()
        self.create_tab2()


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

    def create_tab3(self):
        """
        Creates and initializes all widgets in tab 2.
        @return:
        """
        # Show registered Materials
        tab3Widget = QWidget()
        tab3Layout = QGridLayout()

        Frame2 = QGroupBox("Material")

        self.MaterialNameLabel = QLabel("Name: ")
        self.MaterialNameEdit2 = QLabel("")
        self.MaterialSaveChangesPushButton = QPushButton("Save changes")
        self.MaterialTableWidget = QTableWidget()

        self.MaterialTableWidget.setRowCount(9)
        self.MaterialTableWidget.setColumnCount(4)
        self.MaterialTableWidget.setHorizontalHeaderLabels(['H2', 'CH4', "CO", 'CO2'])
        if unit.unit == 0.750062:
            self.MaterialTableWidget.setVerticalHeaderLabels(
                ["alpha", "eta_ion", "", "", "", 'eta_e', 'eta_ph', 'Cbs [l/m/s]', 'Qth [mbar*l/cm^2/s]'])
        elif unit.unit == 1.33322:
            self.MaterialTableWidget.setVerticalHeaderLabels(
                ["alpha", "eta_ion", "", "", "", 'eta_e', 'eta_ph', 'Cbs [l/m/s]', 'Qth [torr*l/cm^2/s]'])

        frame2Layout = QGridLayout()
        frame2Layout.addWidget(self.MaterialNameLabel, 0, 0, 1, 1)
        frame2Layout.addWidget(self.MaterialNameEdit2, 0, 1, 1, 1)
        frame2Layout.addWidget(self.MaterialSaveChangesPushButton,0,2,1,1)
        frame2Layout.addWidget(self.MaterialTableWidget, 1, 0, 9, 4)
        Frame2.setLayout(frame2Layout)
        Frame2.setMinimumWidth(550)
        Frame2.setMinimumHeight(400)

        Frame1 = QGroupBox("List of Materials")
        self.MaterialsList = self.CreateList(Config.MaterialFolder)
        frame1Layout = QGridLayout()
        frame1Layout.addWidget(self.MaterialsList)
        Frame1.setLayout(frame1Layout)
        Frame1.setFixedWidth(300)

        tab3Layout.addWidget(Frame1, 0, 0)
        tab3Layout.addWidget(Frame2, 0, 1)

        tab3Widget.setLayout(tab3Layout)
        self.tabWidget.addTab(tab3Widget, "View and Edit")


    def populateTable(self):
        """
        Fills the table where the contents of a simulation are shown on selecting an item from the list.
       @return:
       """
        item = self.MaterialsList.currentItem().text()
        self.MaterialNameEdit2.setText(item.split("_")[0])
        Data = ReadComponent(Config.DataFolder + "Input/Materials/" + item + ".csv")

        for i in range(self.MaterialTableWidget.rowCount()):
            for j in range(len(Data[0])):
                self.MaterialTableWidget.setItem(i, j, QTableWidgetItem(str(Data[i][j])))

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

        self.SaveMaterialButton2.clicked.connect(self.SaveCustomMaterial)
        self.MaterialsList.doubleClicked.connect(self.edit_current)
        self.MaterialsList.itemClicked.connect(self.populateTable)
        self.MaterialsList.itemChanged.connect(self.saveNameChanged)
        self.MaterialSaveChangesPushButton.clicked.connect(self.SaveChanges)

    def openDirectoryMaterial(self):
        """
        Opens the directory containing a new Material .
        """

        dir = (
        os.path.dirname(Config.DataFolder + 'Input/'))  # if self.filename is not None else Config.DataFolder+'Input/')
        fname = unicode(QFileDialog.getOpenFileName(self, "Choose CSV-file to upload data", dir))

        self.MaterialEdit.setText(fname)


    def CreateList(self,Dir):
        """
        Creates a list with all the files stored in Dir
        @param Dir: Directory from which the items for the list are extrated.
        @return: listWidget (QListWidget)
        """
        listWidget = QListWidget()
        listWidget.resize(300, 120)

        for c in os.listdir(Dir):
            item = ".".join(c.split(".")[:-1])
            if item == "" and os.path.isdir(Dir + "/" + c):
                item = c
            list_item = QListWidgetItem(item,parent=listWidget)
            list_item.setFlags(list_item.flags() | Qt.ItemIsEditable)
        return listWidget


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

            self.close()
            self.__init__()
            self.show()
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

            self.close()
            self.__init__()
            self.show()

    def edit_current(self):
        """
        Allows the user to change the name of the items of the list
        @return:
        """
        index = self.MaterialsList.currentIndex()
        if index.isValid():
            item = self.MaterialsList.itemFromIndex(index)
            if not item.isSelected():
                item.setSelected(True)
            self.MaterialsList.edit(index)

            self.oldName = item.text()

    def saveNameChanged(self):
        """
        Saves the new name assigned to any item of the list and changes the name of the correspondig simulation to its
        new name
        @return:
        """
        index = self.MaterialsList.currentIndex()
        self.newName = self.MaterialsList.itemFromIndex(index).text()
        os.rename(Config.DataFolder + "Input/Materials/" + self.oldName + ".csv",
                  Config.DataFolder + "Input/Materials/" + str(self.newName) + ".csv")
        self.populateTable()
        self.CreateList(Config.DataFolder + "Input/Materials/")

    def SaveChanges(self):
        """
        Saves changes in an existing simulation
     @  return:
     """
        Data = []
        for i in range(self.MaterialTableWidget.rowCount()):
            column = []
            for j in range(self.MaterialTableWidget.columnCount()):
                column.append(str(self.MaterialTableWidget.item(i,j).text()))
            Data.append(column)
        name = Config.DataFolder + "Input/Materials/" + self.MaterialNameEdit2.text() + ".csv"
        ReWrite(name,Data,horizontal_labels=['H2', 'CH4', "CO", 'CO2'],vertical_labels=["alpha", "eta_ion", "", "", "", 'eta_e', 'eta_ph', 'Cbs [l/m/s]', 'Qth [mbar*l/cm^2/s]'])











if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = NewMatWindow()
    ex.show()
    app.exec_()


