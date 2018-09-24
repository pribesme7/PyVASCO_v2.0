import os
import platform
import sys

from PyQt4.QtCore import (PYQT_VERSION_STR, SIGNAL,QFile, QFileInfo, QSettings,
                          QString, QT_VERSION_STR, QTimer, QVariant, Qt, QDir, QReadLocker, QReadWriteLock, QRectF,)

from PyQt4.QtCore import pyqtSignal as Signal
from PyQt4.QtGui import *
import pyqtgraph as pg  # built on PYQT4 / PySide and numpy
import numpy as np
from Config import Config



#import unit
#from Components import MySimulations,Gassource,Pump
from __init__ import MyMessageBox,ReadComponent,ReWrite


class MySimulationsWindow(QMainWindow):
    """
    'My Simulations' Window launched by the action 'My Simulations' in the menu 'Add and Edit' of PyVASCO.
    """
    def __init__(self, parent=None):
        super(MySimulationsWindow, self).__init__(parent)
        self.tabWidget = QTabWidget()
        self.create_widgets()
        self.msg = MyMessageBox()
        self.setCentralWidget(self.tabWidget)
        self.create_connections()
        self.setWindowTitle("My simulations")
        #self.initiate_window()


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
        # Show registered MySimulationss
        tab1Widget = QWidget()
        tab1Layout = QGridLayout()

        Frame2 = QGroupBox("Simulation")

        self.MySimulationsNameLabel = QLabel("Name: ")
        self.MySimulationsNameEdit = QLabel("")
        self.MySimulationsTableWidget =  QTableWidget()
        self.MySimulationsSavePushButton = QPushButton("Save changes")
        self.MySimulationsTableWidget.setRowCount(8)
        self.MySimulationsTableWidget.setColumnCount(1)
        self.MySimulationsTableWidget.setHorizontalHeaderLabels(["S1"])

        self.MySimulationsTableWidget.setVerticalHeaderLabels(["d [mm]", "L [mm]", "T [K]", "Material", "Pump", 'Gas source', 'Photon flux [photons/m/s]', 'Electron flux [electrons/m/s]'])

        frame2Layout = QGridLayout()
        frame2Layout.addWidget(self.MySimulationsNameLabel,0,0,1,1)
        frame2Layout.addWidget(self.MySimulationsNameEdit, 0, 1,1,1)
        frame2Layout.addWidget(self.MySimulationsTableWidget,1,0,9,4)
        frame2Layout.addWidget(self.MySimulationsSavePushButton, 0,2,1,1)
        Frame2.setLayout(frame2Layout)
        Frame2.setMinimumWidth(550)
        Frame2.setMinimumHeight(400)

        Frame1 = QGroupBox("My simulations")
        self.SimulationsList = self.CreateList(Config.DataFolder + "Input/")
        frame1Layout = QGridLayout()
        frame1Layout.addWidget(self.SimulationsList)
        Frame1.setLayout(frame1Layout)
        Frame1.setFixedWidth(300)

        tab1Layout.addWidget(Frame1,0,0)
        tab1Layout.addWidget(Frame2,0,1)

        tab1Widget.setLayout(tab1Layout)
        self.tabWidget.addTab(tab1Widget, "My simulations")


    def create_tab2(self):
        """
        Creates and initializes all widgets in tab 2.
        """
        tab2Widget = QWidget()

        Frame2 = QGroupBox("Write new simulation")
        self.InputNameLabel = QLabel("Name: ")
        self.InputNameEdit = QLineEdit("")
        self.table_widget = QTableWidget()
        self.AddSegmentPushButton = QPushButton("Add Segment")

        Frame3 = QGroupBox("Save Input")
        self.SaveInputButton2 = QPushButton("Save")

        frame2Layout = QGridLayout()
        frame2Layout.addWidget(self.InputNameLabel, 0, 0)
        frame2Layout.addWidget(self.InputNameEdit, 0, 1)
        frame2Layout.addWidget(self.table_widget, 1, 0, 10, 2)
        frame2Layout.addWidget(self.AddSegmentPushButton, 12, 3)
        self.populate()

        frame3Layout = QGridLayout()
        frame3Layout.addWidget(self.SaveInputButton2)

        tab2Layout = QVBoxLayout()
        Frame2.setLayout(frame2Layout)

        Frame3.setLayout(frame3Layout)
        tab2Layout.addWidget(Frame2)
        tab2Layout.addWidget(Frame3)

        tab2Widget.setLayout(tab2Layout)
        self.tabWidget.addTab(tab2Widget, "Write New Input")
        Frame3.setFixedHeight(75)

    def populate(self):
        """
        Sets number of rows and columns and corresponding labels in the input table.
        """
        self.Segments = ["S1"]
        self.table_widget.setRowCount(8)
        self.table_widget.setColumnCount(len(self.Segments) + 1)
        self.table_widget.setHorizontalHeaderLabels(self.Segments + [""])
        self.table_widget.setVerticalHeaderLabels(
            ["d[mm]", "L[mm]", "T[K]", "Material", "Pump", "Gassource", "Photon flux", "Electron flux"])



    def AddSegment(self):
        """
        Adds a segment in the new input file
        """
        currentSegments = len(self.Segments)
        print currentSegments
        self.Segments += ["S" + str(currentSegments + 1)]
        self.table_widget.setColumnCount(currentSegments + 2)
        self.table_widget.setHorizontalHeaderLabels(self.Segments + [""])
        #  Get the info in the last segment

        for i in range(8):

            try:

                LastRow = str(self.table_widget.item(i, currentSegments).text())
                print LastRow

            except:
                LastRow = ''
            print type(self.table_widget)

            self.table_widget.setItem(i, len(self.Segments), QTableWidgetItem(LastRow))
            self.table_widget.setItem(i, currentSegments, QTableWidgetItem(""))

    def openDirectoryInput(self):
        """
        Opens the directory containing a new Input .
        """

        dir = (
            os.path.dirname(
                Config.DataFolder + 'Input/'))  # if self.filename is not None else Config.DataFolder+'Input/')
        fname = unicode(QFileDialog.getOpenFileName(self, "Choose CSV-file to upload data", dir))

        self.InputEdit.setText(fname)

    def SaveInput(self):
        """
        Creates a file in the corresponding input folder for the Input defined in the tab 'Write New Simulation' of the 'My simulations' window.
        """

        self.InputName = self.InputNameEdit.text()
        if not os.path.isfile(Config.DataFolder + "Input/" + self.InputName + '_New.csv'):
            f = open(Config.DataFolder + "Input/" + self.InputName + '_New.csv', "w")
            f.write(self.InputName + "," + ",".join(self.Segments) + " \n")
            nSegments = len(self.Segments)
            labels = ["d[mm]", "L[mm]", "T[K]", "Material", "Pump", "Gassource", "Photon flux", "Electron flux"]
            print labels
            for i in range(len(labels)):
                cols = []
                for j in range(nSegments + 1):
                    try:
                        c = str(self.table_widget.item(i, j).text())
                        print c
                    except:
                        c = ''
                    cols.append(c)

                cols = ",".join(filter(None, cols)) + "\n"
                print cols
                f.write(labels[i] + "," + cols)
            f.close()
            self.close()
            self.__init__()
            self.show()
        else:

            self.msg.setIcon(QMessageBox.Warning)
            self.msg.setText("This Input already exists! Do you want to overwrite it?")
            self.msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            self.msg.show()
            self.close()
            self.__init__()
            self.show()

    def msgbtn(self, i):
        """
        If the user answers 'Yes', the simulation is overwritten.
        @param i: Signal ('Yes' or 'No') coming from the warning message if the user tries to overwrite an existing file.
        @return: None
        """
        if i.text() == "&Yes":
            f = open(Config.DataFolder + "Input/" + self.InputName + '_New.csv', "w")
            f.write(self.InputName + "," + ",".join(self.Segments) + " \n")
            nSegments = len(self.Segments)
            labels = ["d[mm]", "L[mm]", "T[K]", "Material", "Pump", "Gassource", "Photon flux", "Electron flux"]
            print labels
            for i in range(len(labels)):
                cols = []
                for j in range(nSegments + 1):
                    try:
                        c = str(self.table_widget.item(i, j).text())
                        print c
                    except:
                        c = ''
                    cols.append(c)

                cols = ",".join(filter(None, cols)) + "\n"
                print cols
                f.write(labels[i] + "," + cols)
            f.close()
        else:
            pass

    def CreateList(self, Dir):
        """
        Creates a list with all the files stored in Dir
        @param Dir: Directory from which the items for the list are extrated.
        @return: listWidget (QListWidget)
        """
        listWidget = QListWidget()
        listWidget.resize(300, 120)

        for c in [i.split("_New.")[0] for i in os.listdir(Dir) if i.split("_New.")[-1] == "csv"]:
           
            list_item = QListWidgetItem(c, parent=listWidget)
            list_item.setFlags(list_item.flags() | Qt.ItemIsEditable)
        return listWidget

    def create_connections(self):
        """
        Creates the connections between the GUI widgets and the callback functions.
        """

        print('create_connections')
        # self.unitComboBox.currentIndexChanged.connect(self.unitchange)

        self.AddSegmentPushButton.clicked.connect(self.AddSegment)
        self.SaveInputButton2.clicked.connect(self.SaveInput)
        self.msg.buttonClicked.connect(self.msgbtn)
        self.SimulationsList.doubleClicked.connect(self.edit_current)
        self.SimulationsList.itemClicked.connect(self.populateTable)
        self.SimulationsList.itemChanged.connect(self.saveNameChanged)
        self.MySimulationsSavePushButton.clicked.connect(self.SaveChanges)

    def SaveChanges(self):
        """
        Saves changes in an existing simulation
        @return:
        """
        Data = []
        for i in range(self.MySimulationsTableWidget.rowCount()):
            column = []
            for j in range(self.MySimulationsTableWidget.columnCount()):
                column.append(str(self.MySimulationsTableWidget.item(i,j).text()).replace(" ", ""))
            Data.append(filter(None,column))
        name = Config.DataFolder + "Input/" + self.MySimulationsNameEdit.text() + "_New.csv"
        ReWrite(name,Data,vertical_labels= ["d [mm]", "L [mm]", "T [K]", "Material", "Pump", 'Gas source', 'Photon flux [photons/m/s]','Electron flux [electrons/m/s]'],horizontal_labels = ["S%i" % (i) for i in range(len(Data[0]) - 1)] + [""])

    def edit_current(self):
        """
        Allows the user to change the name of the items of the list
        @return:
        """
        index = self.SimulationsList.currentIndex()
        if index.isValid():
            item = self.SimulationsList.itemFromIndex(index)
            if not item.isSelected():
                item.setSelected(True)
            self.SimulationsList.edit(index)

            self.oldName = item.text()



    def saveNameChanged(self):
        """
        Saves the new name assigned to any item of the list and changes the name of the correspondig simulation to its
        new name
        @return:
        """
        index = self.SimulationsList.currentIndex()
        self.newName = self.SimulationsList.itemFromIndex(index).text()
        os.rename(Config.DataFolder + "Input/" +  self.oldName + "_New.csv",Config.DataFolder + "Input/" +  str(self.newName) + "_New.csv")
        self.populateTable()
        self.CreateList(Config.DataFolder + "Input/")



    def populateTable(self):
        """
         Fills the table where the contents of a simulation are shown on selecting an item from the list.
        @return:
        """
        item = self.SimulationsList.currentItem().text()
        self.MySimulationsNameEdit.setText(item.split("_")[0])
        Data = ReadComponent(Config.DataFolder + "Input/"+ item + "_New.csv" )
        self.MySimulationsTableWidget.setColumnCount(len(Data[0])+1)
        self.MySimulationsTableWidget.setHorizontalHeaderLabels(["S%i"%(i) for i in range(len(Data[0])) ] + [""])
        for i in range(self.MySimulationsTableWidget.rowCount()):
            for j in range(len(Data[0])+1):
                try:
                    self.MySimulationsTableWidget.setItem(i, j, QTableWidgetItem(str(Data[i][j])))
                except:
                    self.MySimulationsTableWidget.setItem(i, j, QTableWidgetItem(""))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MySimulationsWindow()
    ex.show()
    app.exec_()
