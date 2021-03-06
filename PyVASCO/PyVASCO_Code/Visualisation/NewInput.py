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


class NewInputWindow(QMainWindow):
    """
    'New Input File' Window launched by the action 'Input file' in the menu 'Add' of PyVASCO.
    """
    def __init__(self, parent=None):
        super(NewInputWindow, self).__init__(parent)
        self.tabWidget = QTabWidget()
        self.create_widgets()
        self.setCentralWidget(self.tabWidget)
        self.msg = MyMessageBox()
        self.create_connections()
        self.setWindowTitle("New Input")


    def create_widgets(self):
        """
       Calls the methods 'create_tab1()' .
       """
 
        self.create_tab1()

    def create_tab1(self):
        """
        Creates and initializes all widgets in tab 1.
        """
        tab2Widget = QWidget()

        Frame2 = QGroupBox("Write New Input File")
        self.InputNameLabel = QLabel("Name: ")
        self.InputNameEdit = QLineEdit("")
        self.table_widget = QTableWidget()
        self.AddSegmentPushButton = QPushButton("Add Segment")

        Frame3 = QGroupBox("Save Input")
        self.SaveInputButton2 = QPushButton("Save")


        frame2Layout = QGridLayout()
        frame2Layout.addWidget(self.InputNameLabel,0,0)
        frame2Layout.addWidget(self.InputNameEdit,0,1)
        frame2Layout.addWidget(self.table_widget,1,0,10,2)
        frame2Layout.addWidget(self.AddSegmentPushButton,12,3)
        self.populate()

        frame3Layout= QGridLayout()
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
        self.table_widget.setColumnCount(len(self.Segments)+1)
        self.table_widget.setHorizontalHeaderLabels(self.Segments + [""])
        self.table_widget.setVerticalHeaderLabels([ "d[mm]", "L[mm]", "T[K]", "Material", "Pump", "Gassource", "Photon flux", "Electron flux"])



    def create_connections(self):
        """
        Creates the connections between the GUI widgets and the callback functions.
        """

        print('create_connections')
        #self.unitComboBox.currentIndexChanged.connect(self.unitchange)

        self.AddSegmentPushButton.clicked.connect(self.AddSegment)
        self.SaveInputButton2.clicked.connect(self.SaveInput)
        self.msg.buttonClicked.connect(self.msgbtn)

    def AddSegment(self):
        """
        Adds a segment in the new input file
        """
        currentSegments = len(self.Segments)
        print currentSegments
        self.Segments += ["S" + str(currentSegments+1)]
        self.table_widget.setColumnCount(currentSegments + 2)
        self.table_widget.setHorizontalHeaderLabels(self.Segments + [""])
        #  Get the info in the last segment

        for i in range(8):

            try:

                LastRow = str(self.table_widget.item(i, currentSegments).text())
                print LastRow

            except:
                LastRow =''
            print type(self.table_widget)

            self.table_widget.setItem(i, len(self.Segments),QTableWidgetItem(LastRow))
            self.table_widget.setItem(i, currentSegments,QTableWidgetItem(""))


    def openDirectoryInput(self):
        """
        Opens the directory containing a new Input .
        """

        dir = (
        os.path.dirname(Config.DataFolder + 'Input/'))  # if self.filename is not None else Config.DataFolder+'Input/')
        fname = unicode(QFileDialog.getOpenFileName(self, "Choose CSV-file to upload data", dir))

        self.InputEdit.setText(fname)


    def SaveInput(self):
        """
        Creates a file in the corresponding input folder for the Input defined in the tab 'Write New Input' of the 'New Input' window.
        """

        self.InputName = self.InputNameEdit.text()
        if not os.path.isfile(Config.DataFolder +"Input/"+ self.InputName+ '_New.csv'):
            f = open(Config.DataFolder +"Input/"+ self.InputName+ '_New.csv', "w")
            f.write(self.InputName + "," + ",".join(self.Segments) + " \n")
            nSegments = len(self.Segments)
            labels = [ "d[mm]", "L[mm]", "T[K]", "Material", "Pump", "Gassource", "Photon flux", "Electron flux"]
            print labels
            for i in range(len(labels)):
                cols = []
                for j in range(nSegments+1):
                    try:
                        c = str(self.table_widget.item(i,j).text())
                        print c
                    except:
                        c = ''
                    cols.append(c)

                cols =  ",".join(filter(None,cols)) + "\n"
                print cols
                f.write(labels[i] + "," + cols)
            f.close()

        else:

            self.msg.setIcon(QMessageBox.Warning)
            self.msg.setText("This Input already exists! Do you want to overwrite it?")
            self.msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            self.msg.show()


    def msgbtn(self,i):
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

                cols = ",".join(filter(None,cols)) + "\n"
                print cols
                f.write(labels[i] + "," + cols)
            f.close()
        else:
            pass











if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = NewInputWindow()
    ex.show()
    app.exec_()


