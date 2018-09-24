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
from Components.Gassource import Gassource
from Visualisation import MyMessageBox
from Visualisation import MyMessageBox,ReadComponent,ReWrite

class NewGSourceWindow(QMainWindow):
    """
   'New Gas Source' Window launched by the action 'Gassource' in the menu 'Add' of PyVASCO.
   """
    def __init__(self, parent=None):
        super(NewGSourceWindow, self).__init__(parent)
        self.tabWidget = QTabWidget()
        self.create_widgets()
        self.setCentralWidget(self.tabWidget)
        self.create_connections()
        self.setWindowTitle("New Gas Source")


    def create_widgets(self):
        """
       Calls the methods 'create_tab1()' and 'create_tab2()' .
       """
        self.create_tab3()
        self.create_tab2()


    def create_tab2(self):
        """
       Creates and initializes all widgets in tab 2.
       """
        tab2Widget = QWidget()

        Frame2 = QGroupBox("Write New Gas Source")
        self.GasSourceNameLabel = QLabel("New Gas Source Name: ")
        self.GasSourceNameEdit = QLineEdit("")
        self.table_widget = QTableWidget()


        Frame3 = QGroupBox("Save Gas Source")
        self.SaveGasSourceButton2 = QPushButton("Save")


        frame2Layout = QGridLayout()
        frame2Layout.addWidget(self.GasSourceNameLabel,0,0)
        frame2Layout.addWidget(self.GasSourceNameEdit,0,1)
        frame2Layout.addWidget(self.table_widget,1,0,10,2)
        self.populate()

        frame3Layout= QGridLayout()
        frame3Layout.addWidget(self.SaveGasSourceButton2)


        tab2Layout = QVBoxLayout()
        Frame2.setLayout(frame2Layout)

        Frame3.setLayout(frame3Layout)
        tab2Layout.addWidget(Frame2)
        tab2Layout.addWidget(Frame3)

        tab2Widget.setLayout(tab2Layout)
        self.tabWidget.addTab(tab2Widget, "Write New GasSource")
        Frame3.setFixedHeight(75)



    def create_tab3(self):
        """
         Creates and initializes all widgets in tab 3.
        """
        # Show registered GasSources
        tab3Widget = QWidget()
        tab3Layout = QGridLayout()

        Frame2 = QGroupBox("GasSource")

        self.GasSourceNameLabel = QLabel("Name: ")
        self.GasSourceNameEdit2 = QLabel("")
        self.GasSourceSaveChangesPushButton = QPushButton("Save changes")
        self.GasSourceTableWidget = QTableWidget()

        self.GasSourceTableWidget.setRowCount(4)
        self.GasSourceTableWidget.setColumnCount(1)
        self.GasSourceTableWidget.setHorizontalHeaderLabels([""])

        self.GasSourceTableWidget.setVerticalHeaderLabels(
                ["g_H2 [mbar l/s]", "g_CH4 [mbar l/s]", "g_CO [mbar l/s]", "g_CO2 [mbar l/s]"])

        frame2Layout = QGridLayout()
        frame2Layout.addWidget(self.GasSourceNameLabel, 0, 0, 1, 1)
        frame2Layout.addWidget(self.GasSourceNameEdit2, 0, 1, 1, 1)
        frame2Layout.addWidget(self.GasSourceSaveChangesPushButton, 0, 2, 1, 1)
        frame2Layout.addWidget(self.GasSourceTableWidget, 1, 0, 9, 4)
        Frame2.setLayout(frame2Layout)
        Frame2.setMinimumWidth(550)
        Frame2.setMinimumHeight(400)

        Frame1 = QGroupBox("List of GasSources")
        self.GasSourcesList = self.CreateList(Config.GassourceFolder)
        frame1Layout = QGridLayout()
        frame1Layout.addWidget(self.GasSourcesList)
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
        item = self.GasSourcesList.currentItem().text()
        self.GasSourceNameEdit2.setText(item.split("_")[0])
        Data = ReadComponent(Config.GassourceFolder+ item + ".csv")
        # self.GasSourceTableWidget.setHorizontalHeaderLabels(['H2', 'CH4', "CO", 'CO2'])
        for i in range(self.GasSourceTableWidget.rowCount()):
            for j in range(len(Data[0])):
                self.GasSourceTableWidget.setItem(i, j, QTableWidgetItem(str(Data[i][j])))

    def openDirectoryGasSource(self):
        """
        Opens the directory containing a new GasSource .
        """

        dir = (
            os.path.dirname(
                Config.DataFolder + 'Input/'))  # if self.filename is not None else Config.DataFolder+'Input/')
        fname = unicode(QFileDialog.getOpenFileName(self, "Choose CSV-file to upload data", dir))

        self.GasSourceEdit.setText(fname)


    def CreateList(self, Dir):

        listWidget = QListWidget()
        listWidget.resize(300, 120)

        for c in os.listdir(Dir):
            item = ".".join(c.split(".")[:-1])
            if item == "" and os.path.isdir(Dir + "/" + c):
                item = c
            list_item = QListWidgetItem(item, parent=listWidget)
            list_item.setFlags(list_item.flags() | Qt.ItemIsEditable)
        return listWidget

    def populate(self):
        """
        Sets number of rows and columns and corresponding labels in the input table.
        """
        self.table_widget.setRowCount(4)
        self.table_widget.setColumnCount(1)
        self.table_widget.setVerticalHeaderLabels([ "g_H2 [mbar l/s]", "g_CH4 [mbar l/s]","g_CO [mbar l/s]",
                                                    "g_CO2 [mbar l/s]"])

    def create_connections(self):
        """
        Creates the connections between the GUI widgets and the callback functions.
        """

        print('create_connections')

        self.SaveGasSourceButton2.clicked.connect(self.SaveCustomGasSource)
        self.GasSourcesList.doubleClicked.connect(self.edit_current)
        self.GasSourcesList.itemClicked.connect(self.populateTable)
        self.GasSourcesList.itemChanged.connect(self.saveNameChanged)
        self.GasSourceSaveChangesPushButton.clicked.connect(self.SaveChanges)

    def SaveCustomGasSource(self):
        """
        Creates a file in the corresponding input folder for the gas source defined in the tab 'Write new GasSource' of the 'New Gas Source' window.
        """
        self.GasSourceName = self.GasSourceNameEdit.text()
        if not os.path.isfile(Config.GassourceFolder + self.GasSourceName + ".csv"):
            f = open(Config.GassourceFolder + self.GasSourceName + ".csv", "w")
            f.write(self.GasSourceName + " \n")
            labels = [ "g_H2 [mbar l/s]", "g_CH4 [mbar l/s]","g_CO [mbar l/s]","g_CO2 [mbar l/s]"]
            print labels
            for i in range(4):
                cols = str(self.table_widget.item(i,0).text()) + "\n"
                f.write(labels[i] + "," + cols)
            f.close()
            Config.LoadGassource()
            self.close()
            self.__init__()
            self.show()
        else:
            def msgbtn(i):
                print i.text()
                if i.text() == "&Yes":
                    f = open(Config.GassourceFolder + self.GasSourceName + ".csv", "w")
                    f.write(self.GasSourceName + " \n")
                    print self.GasSourceName + " \n"
                    labels = ["g_H2 [mbar l/s]", "g_CH4 [mbar l/s]", "g_CO [mbar l/s]", "g_CO2 [mbar l/s]"]
                    print labels
                    for i in range(4):
                        cols = str(self.table_widget.item(i, 0).text()) + "\n"
                        f.write(labels[i] + "," + cols)
                        print labels[i] + "," + cols
                    f.close()

                    Config.LoadGassource()
                    self.__init__()
                else:
                    pass
            msg = MyMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("This GasSource already exists! \n Do you want to overwrite it?")

            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.buttonClicked.connect(msgbtn)
            msg.exec_()

    def edit_current(self):
        """
       Allows the user to change the name of the items of the list
       @return:
       """
        index = self.GasSourcesList.currentIndex()
        if index.isValid():
            item = self.GasSourcesList.itemFromIndex(index)
            if not item.isSelected():
                item.setSelected(True)
            self.GasSourcesList.edit(index)

            self.oldName = item.text()

    def saveNameChanged(self):
        """
        Saves the new name assigned to any item of the list and changes the name of the correspondig simulation to its
        new name
        @return:
        """
        index = self.GasSourcesList.currentIndex()
        self.newName = self.GasSourcesList.itemFromIndex(index).text()
        os.rename(Config.GassourceFolder + self.oldName + ".csv",
                  Config.GassourceFolder + str(self.newName) + ".csv")
        self.populateTable()
        self.GasSourcesList = self.CreateList(Config.GassourceFolder)


    def SaveChanges(self):
        """
        Saves changes in an existing gas source
        @return:
        """
        Data = []
        for i in range(self.GasSourceTableWidget.rowCount()):
            column = []
            for j in range(self.GasSourceTableWidget.columnCount()):
                column.append(str(self.GasSourceTableWidget.item(i, j).text()))
            Data.append(column)
        name = Config.GassourceFolder + self.GasSourceNameEdit2.text() + ".csv"
        Data = [d[0] for d in Data]
        ReWrite(name, Data, horizontal_labels=[""],
                vertical_labels=["g_H2 [mbar l/s]","g_CH4 [mbar l/s]","g_CO [mbar l/s]","g_CO2 [mbar l/s]"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = NewGSourceWindow()
    ex.show()
    app.exec_()


