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
from Components.Pump import Pump
from Visualisation import MyMessageBox,ReadComponent,ReWrite


def WritePump(File,Array,Name):
    """
    Writes the pumping speed of a pump identified with 'Name' in the file 'File'  
    @param  File: (str) File where the pump information will be written.
    @param  Array: (np.ndarray) Array containing the pumping speeds of the pump for the different gas species
    @param  Name: (str) Name of the pump
    @return:
    """
    f = open(File, "w")
    f.write(Name + ", \n")
    labels = ["S_H2 [l/s]", "S_CH4 [l/s]", "S_CO [l/s]", "S_CO2 [l/s]"]
    print labels
    Array = np.array(Array).T.tolist()
    for i in range(4):
        if type(Array[i])==list:
            cols = ",".join(Array[i]) + "\n"
        else:
            cols = str(Array[i]) + "\n"
        f.write(labels[i] + "," + cols)
    f.close()


def eformat(f, prec, exp_digits):
    """
    Writes a number in scientific format with a specified precission
    @param f: number to express in scientific format
    @param prec: (int) precission of the decimal part
    @param exp_digits: (int) precission of the exponent
    @return: (str) Input number in scientific format with
    """
    s = "%.*e" % (prec, f)
    mantissa, exp = s.split('e')
    # add 1 to digits as 1 is taken by sign +/-
    return "%sE%+0*d" % (mantissa, exp_digits + 1, int(exp))


class NewPumpWindow(QMainWindow):
    """
    'New Pump' Window launched by the action 'Pump' in the menu 'Add' of PyVASCO.
    """

    def __init__(self, parent=None):
        super(NewPumpWindow, self).__init__(parent)
        self.tabWidget = QTabWidget()
        self.create_widgets()
        self.setCentralWidget(self.tabWidget)
        self.create_connections()
        self.setWindowTitle("New Pump")


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

        Frame2 = QGroupBox("Write New Pump")
        self.PumpNameLabel = QLabel("New Pump Name: ")
        self.PumpNameEdit = QLineEdit("")
        self.table_widget = QTableWidget()

        self.AddSpeedLabel = QPushButton("Add pumping speed p [mbar]: ")

        self.AddSpeedEdit  = QLineEdit("")
        self.AddSpeedEdit.setMaximumHeight(self.AddSpeedLabel.sizeHint().height()*1.5)

        Frame3 = QGroupBox("Save Pump")
        self.SavePumpButton2 = QPushButton("Save")


        frame2Layout = QGridLayout()
        frame2Layout.addWidget(self.PumpNameLabel,0,0)
        frame2Layout.addWidget(self.PumpNameEdit,0,1)
        frame2Layout.addWidget(self.table_widget,1,0,4,2)
        frame2Layout.addWidget(self.AddSpeedLabel,5,0,1,1)
        frame2Layout.addWidget(self.AddSpeedEdit, 5,1,1,1)
        self.populate()

        frame3Layout= QGridLayout()
        frame3Layout.addWidget(self.SavePumpButton2)


        tab2Layout = QVBoxLayout()
        Frame2.setLayout(frame2Layout)

        Frame3.setLayout(frame3Layout)
        tab2Layout.addWidget(Frame2)
        tab2Layout.addWidget(Frame3)

        tab2Widget.setLayout(tab2Layout)
        self.tabWidget.addTab(tab2Widget, "Write New Pump")
        Frame3.setFixedHeight(75)

    def create_tab3(self):
        """
        Creates and initializes all widgets in tab 3.
        """
        # Show registered Pumps
        tab3Widget = QWidget()
        tab3Layout = QGridLayout()

        Frame2 = QGroupBox("Pump")

        self.PumpNameLabel = QLabel("Name: ")
        self.PumpNameEdit2 = QLabel("")
        self.PumpSaveChangesPushButton = QPushButton("Save changes")
        self.PumpTableWidget = QTableWidget()
        self.PumpTableWidget.setRowCount(4)
        self.PumpTableWidget.setColumnCount(1)
        self.PumpTableWidget.setVerticalHeaderLabels(["S_H2 [l/s]", "S_CH4 [l/s]", "S_CO [l/s]", "S_CO2 [l/s]"])
        self.PumpTableWidget.setHorizontalHeaderLabels(["Nominal"])
        frame2Layout = QGridLayout()
        frame2Layout.addWidget(self.PumpNameLabel, 0, 0, 1, 1)
        frame2Layout.addWidget(self.PumpNameEdit2, 0, 1, 1, 1)
        frame2Layout.addWidget(self.PumpSaveChangesPushButton, 0, 2, 1, 1)
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

        tab3Layout.addWidget(Frame1, 0, 0)
        tab3Layout.addWidget(Frame2, 0, 1)

        tab3Widget.setLayout(tab3Layout)
        self.tabWidget.addTab(tab3Widget, "View and Edit")

    def CreateList(self, Dir):
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
            list_item = QListWidgetItem(item, parent=listWidget)
            list_item.setFlags(list_item.flags() | Qt.ItemIsEditable)

        return listWidget

    def populateTable(self):
        """
         Fills the table where the contents of a simulation are shown on selecting an item from the list.
         @return:
        """
        item = self.PumpsList.currentItem().text()
        if os.path.isfile(Config.PumpFolder + item + ".csv"):
            self.PumpTableWidget.setColumnCount(1)
            self.PumpTableWidget.setHorizontalHeaderLabels(["Nominal"])
            Data = ReadComponent(Config.PumpFolder + item + ".csv")
            self.PumpNameEdit2.setText(item)
            for i in range(self.PumpTableWidget.rowCount()):
                for j in range(self.PumpTableWidget.columnCount()):
                    self.PumpTableWidget.setItem(i, j, QTableWidgetItem(str(Data[i][j])))
        else:
            Data = ReadComponent(str(Config.PumpFolder + item))
            self.PumpNameEdit2.setText(item)
            keys = ["Nominal"] + [k for k in Data.keys() if k != "Nominal"]
            labels = ["Nominal"] + [k + " mbar" for k in Data.keys() if k != "Nominal"]
            self.Labels = keys
            self.PumpTableWidget.setColumnCount(len(keys))
            self.PumpTableWidget.setHorizontalHeaderLabels(labels)
            for j, k in enumerate(keys):
                for i in range(4):
                    self.PumpTableWidget.setItem(i, j, QTableWidgetItem(str(Data[k][i][0])))



    def populate(self):
        """
        Sets number of rows and columns and corresponding labels in the input table.
        """

        self.table_widget.setRowCount(4)
        self.table_widget.setColumnCount(1)
        self.Labels = ["Nominal"]
        self.table_widget.setHorizontalHeaderLabels(self.Labels)
        self.table_widget.setVerticalHeaderLabels([ "S_H2 [l/s]", "S_CH4 [l/s]","S_CO [l/s]","S_CO2 [l/s]"])
        for i in range(4):
            self.table_widget.setItem(i,0,QTableWidgetItem(""))
        self.AddSpeedEdit.setText("")

    def create_connections(self):
        """
        Creates the connections between the GUI widgets and the callback functions.
        """

        print('create_connections')
        self.SavePumpButton2.clicked.connect(self.SaveCustomPump)
        self.AddSpeedLabel.clicked.connect(self.AddSpeedColumn)
        self.PumpNameEdit.editingFinished.connect(self.handleEditingFinished)
        self.PumpsList.doubleClicked.connect(self.edit_current)
        self.PumpsList.itemClicked.connect(self.populateTable)
        self.PumpsList.itemChanged.connect(self.saveNameChanged)
        self.PumpSaveChangesPushButton.clicked.connect(self.SaveChanges)

    def handleEditingFinished(self):
        """
         If a new pump identifier is written, the table below will be reseted
        """
        if self.PumpNameEdit.isModified():
            print "Writing new pump! "
            self.populate()

    def openDirectoryPump(self):
        """
        Opens the directory containing a new pump .
        """

        dir = (
        os.path.dirname(Config.DataFolder + 'Input/'))  # if self.filename is not None else Config.DataFolder+'Input/')
        fname = unicode(QFileDialog.getOpenFileName(self, "Choose CSV-file to upload data", dir))

        self.PumpEdit.setText(fname)

    def AddSpeedColumn(self):
        n = self.table_widget.columnCount()

        self.Labels += [eformat(float(self.AddSpeedEdit.text()),0, 1) + " mbar"]
        self.table_widget.setColumnCount(n+1)
        self.table_widget.setHorizontalHeaderLabels(self.Labels)


    def SaveCustomPump(self):
        """
        Creates a file in the corresponding input folder for the Pump defined in the tab 'Write New Pump' of the 'New Pump' window.
        """

        self.PumpName = self.PumpNameEdit.text()

        if (not os.path.isfile(Config.PumpFolder + self.PumpName + ".csv")) and (not os.path.isdir(Config.PumpFolder + self.PumpName)):
            if self.table_widget.columnCount() == 1:
                Array = [str(self.table_widget.item(i, 0).text()) for i in range(4)]
                WritePump(Config.PumpFolder + self.PumpName + ".csv", Array,self.PumpName)
                Config.LoadPumps()
                self.close()
                self.__init__()
                self.show()
            else:
                labels = ["Nominal"] + [l.split(" ")[0] for l in self.Labels if l != "Nominal"]
                Array = [[str(self.table_widget.item(i, j).text()) for i in range(4)] for j in range(len(labels))]
                os.mkdir(Config.PumpFolder + self.PumpName)
                for i,l in enumerate(labels):
                    try:
                        l = eformat(float(l),0,1)
                    except:
                        pass
                    WritePump(Config.PumpFolder + self.PumpName + "/" + self.PumpName +"_" +  l + ".csv", Array[i], self.PumpName)
                Config.LoadPumps()
                self.close()
                self.__init__()
                self.show()
        else:
            def msgbtn(i):
                print i.text()
                if i.text() == "&Yes":
                    f = open(Config.PumpFolder + self.PumpName + ".csv", "w")
                    f.write(self.PumpName + " \n")
                    print self.PumpName + " \n"
                    labels = ["S_H2 [l/s]", "S_CH4 [l/s]", "S_CO [l/s]", "S_CO2 [l/s]"]
                    print labels
                    for i in range(4):
                        cols = str(self.table_widget.item(i, 0).text()) + "\n"
                        f.write(labels[i] + "," + cols)
                        print labels[i] + "," + cols
                    f.close()

                    Config.LoadPumps()
                else:
                    pass
            msg = MyMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("This Pump already exists! \n Do you want to overwrite it?")

            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.buttonClicked.connect(msgbtn)
            msg.exec_()

    def edit_current(self):
        """
        Allows the user to change the name of the items of the list
        @return:
        """
        index = self.PumpsList.currentIndex()
        if index.isValid():
            item = self.PumpsList.itemFromIndex(index)
            if not item.isSelected():
                item.setSelected(True)
            self.PumpsList.edit(index)

            self.oldName = item.text()


    def SaveChanges(self):
        """
                Saves changes in an existing simulation
                 @return:
                 """
        Data = []
        if self.PumpTableWidget.columnCount() > 1:
            print "Complex pump!"
            for j in range(self.PumpTableWidget.columnCount()):
                row = []
                for i in range(self.PumpTableWidget.rowCount()):
                    row.append(str(self.PumpTableWidget.item(i,j).text()))
                name = Config.PumpFolder + self.PumpNameEdit2.text() + "/"+  self.PumpNameEdit2.text()+"_" + self.Labels[j]+ ".csv"
                ReWrite(name, row, vertical_labels=["S_H2 [l/s]", "S_CH4 [l/s]", "S_CO [l/s]", "S_CO2 [l/s]"],
                        horizontal_labels=self.Labels[j])


        else:
            for i in range(self.PumpTableWidget.rowCount()):
                column = []
                for j in range(self.PumpTableWidget.columnCount()):
                    column.append(str(self.PumpTableWidget.item(i,j).text()))
                Data.append(column)


            name = Config.PumpFolder+ self.PumpNameEdit2.text() + ".csv"
            Data = [d[0] for d in Data]
            ReWrite(name,Data,vertical_labels= ["S_H2 [l/s]", "S_CH4 [l/s]","S_CO [l/s]","S_CO2 [l/s]"],horizontal_labels =self.Labels)


    def saveNameChanged(self):
        index = self.PumpsList.currentIndex()
        self.newName = self.PumpsList.itemFromIndex(index).text()
        if len(self.Labels) > 1 :
            print "complex pump! ", self.Labels
            for f in os.listdir(Config.PumpFolder + self.oldName + "/"):
                ending = f.split(self.oldName)[1]
                os.rename(Config.PumpFolder + self.oldName + "/" + f,Config.PumpFolder + self.oldName + "/" + self.newName + ending  )
            os.rename(Config.PumpFolder + self.oldName,Config.PumpFolder + self.newName)
        else:
            os.rename(Config.PumpFolder + self.oldName + ".csv", Config.PumpFolder + self.newName + ".csv")

        self.populateTable()
        self.CreateList(Config.DataFolder + "Input/Materials/")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = NewPumpWindow()
    ex.show()
    app.exec_()


