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
from Visualisation import MyMessageBox


def WritePump(File,Array,Name):
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
        infoLabel = QLabel("Select new pump from file")

        self.PumpEdit = QLineEdit()
        self.PumpButton = QPushButton("Directory")
        self.SavePumpButton = QPushButton("Save Pump")

        frame1Layout = QGridLayout()  # how the items within one frame are aligned
        frame1Layout.addWidget(infoLabel, 0, 0)
        frame1Layout.addWidget(self.PumpButton, 1,0)
        frame1Layout.addWidget(self.PumpEdit, 1,1)
        frame1Layout.addWidget(self.SavePumpButton, 2, 1)

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

    def initiate_window(self):
        pass

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
        #self.unitComboBox.currentIndexChanged.connect(self.unitchange)
        self.PumpButton.clicked.connect(self.openDirectoryPump)
        self.SavePumpButton.clicked.connect(self.SavePump)
        self.SavePumpButton2.clicked.connect(self.SaveCustomPump)
        self.AddSpeedLabel.clicked.connect(self.AddSpeedColumn)
        self.PumpNameEdit.editingFinished.connect(self.handleEditingFinished)

    def handleEditingFinished(self):
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


    def SavePump(self):
        """
        Copies the file containg the new Pump in the corresponding directory, so it will be properly detected by the PyVASCO. In case of error, launches a warning message.
        """

        f = open(self.PumpEdit.text())
        lines = f.readlines()
        f.close()
        lines = [l.strip("\n").split(",") for l in lines]
        print lines
        self.PumpName = lines[0][0]
        if (lines[1][0] != "S_H2 [l/s]" or lines[2][0] != "S_CH4 [l/s]" or lines[3][0] != "S_CO [l/s]" or \
            lines[4][0] != "S_CO2 [l/s]" or self.PumpName == ""):
            msg = MyMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Wrong format for pump! ")
            msg.setWindowTitle("Pump Warning Bow")
            msg.setDetailedText("A Pump file should be a CSV file with the following structure: \n\n"
                                "| Name of the pump |     \n"
                                "|------------------|---    \n"
                                "|   S_H2 [l/s]     |      \n"
                                "|------------------|---    \n"
                                "|   S_CH4 [l/s]    |      \n"
                                "|------------------|---    \n"
                                "|   S_CO [l/s]     |      \n"
                                "|------------------|---    \n"
                                "|   S_CO2 [l/s]     |      \n"
                                "|------------------|---    \n")

            msg.exec_()

        else:
            name = os.path.split(self.PumpEdit.text())
            if name[0] != Config.PumpFolder:
                NewPump = os.path.join(Config.PumpFolder, name[1])
                os.rename(name, NewPump)
            else:
                NewPump = self.PumpEdit.text()

            NewPump = Pump(NewPump)
            Config.Config.LoadPumps()

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




if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = NewPumpWindow()
    ex.show()
    app.exec_()


