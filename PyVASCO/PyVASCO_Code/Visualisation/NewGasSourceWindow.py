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
        infoLabel = QLabel("Select new Gas Source from file")

        self.GasSourceEdit = QLineEdit()
        self.GasSourceButton = QPushButton("Directory")
        self.SaveGasSourceButton = QPushButton("Save Gas Source")

        frame1Layout = QGridLayout()  # how the items within one frame are aligned
        frame1Layout.addWidget(infoLabel, 0, 0)
        frame1Layout.addWidget(self.GasSourceButton, 1,0)
        frame1Layout.addWidget(self.GasSourceEdit, 1,1)
        frame1Layout.addWidget(self.SaveGasSourceButton, 2, 1)

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

    def initiate_window(self):
        pass

    def populate(self):
        """
        Sets number of rows and columns and corresponding labels in the input table.
        """
        self.table_widget.setRowCount(4)
        self.table_widget.setColumnCount(1)
        self.table_widget.setVerticalHeaderLabels([ "g_H2 [mbar *l/s]", "g_CH4 [mbar *l/s]","g_CO [mbar *l/s]",
                                                    "g_CO2 [mbar *l/s]"])

    def create_connections(self):
        """
        Creates the connections between the GUI widgets and the callback functions.
        """
        print('create_connections')
        #self.unitComboBox.currentIndexChanged.connect(self.unitchange)
        self.GasSourceButton.clicked.connect(self.openDirectoryGasSource)
        self.SaveGasSourceButton.clicked.connect(self.SaveGasSource)
        self.SaveGasSourceButton2.clicked.connect(self.SaveCustomGasSource)

    def openDirectoryGasSource(self):
        """
        Opens the directory containing a new type of Gas source .
        """
        dir = (
        os.path.dirname(Config.DataFolder + 'Input/'))  # if self.filename is not None else Config.DataFolder+'Input/')
        fname = unicode(QFileDialog.getOpenFileName(self, "Choose CSV-file to upload data", dir))

        self.GasSourceEdit.setText(fname)

    def SaveGasSource(self):
        """
        Copies the file containg the new gas source in the corresponding directory, so it will be properly detected by the PyVASCO. In case of error, launches a warning message.
        """

        f = open(self.GasSourceEdit.text())
        lines = f.readlines()
        f.close()
        lines = [l.strip("\n").split(",") for l in lines]
        print lines
        self.GasSourceName = lines[0][0]
        if (lines[1][0] != "g_H2 [mbar *l/s]" or lines[2][0] != "g_CH4 [mbar *l/s]" or lines[3][0] != "g_CO [mbar *l/s]" or \
            lines[4][0] != "g_CO2 [mbar *l/s]" or self.GasSourceName == ""):
            msg = MyMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Wrong format for GasSource! ")
            msg.setWindowTitle("GasSource Warning Bow")
            msg.setDetailedText("A GasSource file should be a CSV file with the following structure: \n\n"
                                "| Name of the GasSource |     \n"
                                "|------------------|---    \n"
                                "|   g_H2 [mbar *l/s]     |      \n"
                                "|------------------|---    \n"
                                "|   g_CH4 [mbar *l/s]    |      \n"
                                "|------------------|---    \n"
                                "|   g_CO [mbar *l/s]     |      \n"
                                "|------------------|---    \n"
                                "|   g_CO2 [mbar *l/s]     |      \n"
                                "|------------------|---    \n")

            msg.exec_()

        else:
            name = os.path.split(self.GasSourceEdit.text())
            if name[0] != Config.GassourceFolder:
                NewGasSource = os.path.join(Config.GassourceFolder, name[1])
                os.rename(name, NewGasSource)
            else:
                NewGasSource = self.GasSourceEdit.text()

            NewGasSource = Gassource(NewGasSource)
            Config.Config.LoadGassource()

    def SaveCustomGasSource(self):
        """
        Creates a file in the corresponding input folder for the gas source defined in the tab 'Write new GasSource' of the 'New Gas Source' window.
        """
        self.GasSourceName = self.GasSourceNameEdit.text()
        if not os.path.isfile(Config.GassourceFolder + self.GasSourceName + ".csv"):
            f = open(Config.GassourceFolder + self.GasSourceName + ".csv", "w")
            f.write(self.GasSourceName + " \n")
            labels = [ "g_H2 [l/s]", "g_CH4 [l/s]","g_CO [l/s]","g_CO2 [l/s]"]
            print labels
            for i in range(4):
                cols = str(self.table_widget.item(i,0).text()) + "\n"
                f.write(labels[i] + "," + cols)
            f.close()
            Config.LoadGassource()
        else:
            def msgbtn(i):
                print i.text()
                if i.text() == "&Yes":
                    f = open(Config.GassourceFolder + self.GasSourceName + ".csv", "w")
                    f.write(self.GasSourceName + " \n")
                    print self.GasSourceName + " \n"
                    labels = ["g_H2 [l/s]", "g_CH4 [l/s]", "g_CO [l/s]", "g_CO2 [l/s]"]
                    print labels
                    for i in range(4):
                        cols = str(self.table_widget.item(i, 0).text()) + "\n"
                        f.write(labels[i] + "," + cols)
                        print labels[i] + "," + cols
                    f.close()

                    Config.LoadGassource()
                else:
                    pass
            msg = MyMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("This GasSource already exists! \n Do you want to overwrite it?")

            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.buttonClicked.connect(msgbtn)
            msg.exec_()











if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = NewGSourceWindow()
    ex.show()
    app.exec_()


