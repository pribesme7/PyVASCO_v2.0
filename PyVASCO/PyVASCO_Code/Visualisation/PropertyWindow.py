import os
import platform
import sys

from PyQt4.QtCore import (PYQT_VERSION_STR, QFile, QFileInfo, QSettings,
        QString, QT_VERSION_STR, QTimer, QVariant, Qt,QDir, QReadLocker, QReadWriteLock, QRectF)
from PyQt4.QtCore import pyqtSignal as Signal
from PyQt4.QtGui import *
import pyqtgraph as pg #built on PYQT4 / PySide and numpy
import numpy as np
import Config
from Config import Config
import unit

class PropWindow(QMainWindow):
    """
    'Properties' Window launched by the action 'Properties' in the menu 'File' of PyVASCO.
    """

    def __init__(self, parent=None):
        super(PropWindow, self).__init__(parent)

        self.create_widgets()
        self.setCentralWidget(self.Frame1)
        self.create_connections()
        self.setWindowTitle("Properties:")
        self.initiate_window()

    def create_widgets(self):
        """
        Creates and initializes all widgets in the window.
        """
        self.Frame1=QGroupBox("Upload external data:")

        #widgets for FRAME 1 
        unitLabel = QLabel("Choose the unit for input files:")
        self.unitComboBox = QComboBox()
        self.unitComboBox.addItems(["mbar","torr"])
        
        # +++++++++++ LAYOUT
        frame1Layout=QGridLayout() # how the items within one frame are aligned
        frame1Layout.addWidget(unitLabel,0,0)
        frame1Layout.addWidget(self.unitComboBox,0,1)
        self.Frame1.setLayout(frame1Layout)
    
    def initiate_window(self):
        """
        Initilizes the state of the windows.
        """
        print(' initiate_window')
        print(unit.unit)
        if unit.unit == 0.750062:
            self.unitComboBox.setCurrentIndex(0)
        else: self.unitComboBox.setCurrentIndex(1)

    def create_connections(self):
        """
        Creates the connections between the GUI widgets and the callback functions.
        """

        print('create_connections')
        self.unitComboBox.currentIndexChanged.connect(self.unitchange)
            

    #Functions for connections:
    def unitchange(self):
        """
        Sets the unit of the outgassing rate and of the gas sources to be mbar if 'mbar' is selected and to be torr if
        'torr' is selected. If torr is selected, the outgassing rate and gas sources are transformed to mbar.
        """
        #the unit combobox indicated in which unit the data is uploaded! Then the data is cocnverted into density.
        print(' unitchange')
       
        if self.unitComboBox.currentText() == 'mbar' and unit.unit == 1.33322:
            unit.unit = unit.setUnit(0.750062)
            for M in list(Config.Materials.values()):
                M.OutGassing = np.array([x*unit.unit for x in M.OutGassing])
            for G in list(Config.Gassources.values()):
                G.GasRelease = np.array([x*unit.unit for x in G.GasRelease])

        elif self.unitComboBox.currentText() == 'torr' and unit.unit == 0.750062:

            unit.unit = unit.setUnit(1.33322)
            for M in list(Config.Materials.values()):
                M.OutGassing = np.array([x*unit.unit for x in M.OutGassing])
            for G in list(Config.Gassources.values()):
                G.GasRelease = np.array([x*unit.unit for x in G.GasRelease])

        else: print ' units were not changed!'

        




if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = PropWindow()
    ex.show()
    app.exec_()
    

