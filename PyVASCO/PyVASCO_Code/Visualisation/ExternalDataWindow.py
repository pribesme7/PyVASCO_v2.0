import os
import platform
import sys

from PyQt4.QtCore import (PYQT_VERSION_STR, QFile, QFileInfo, QSettings,
        QString, QT_VERSION_STR, QTimer, QVariant, Qt,QDir, QReadLocker, QReadWriteLock, QRectF)
from PyQt4.QtCore import pyqtSignal as Signal
from PyQt4.QtGui import *
import pyqtgraph as pg #built on PYQT4 / PySide and numpy

from Config import Config

class ExDataWindow(QMainWindow):


    def __init__(self, parent=None):
        super(ExDataWindow, self).__init__(parent)

        self.create_widgets()
        self.setCentralWidget(self.Frame1)
        self.create_connections()
        self.setWindowTitle("Upload external data")
        self.initiate_window()

    def create_widgets(self):
        self.Frame1=QGroupBox("Upload external data:")
        
 

        #widgets for FRAME 1 
        infoLabel = QLabel("Define Parameters with a distribution")
        self.OutgassingCheckBox = QCheckBox("Outgassing")
        self.OutgassingEdit = QLineEdit()
        self.OutgassingButton = QPushButton("Directory")

        self.PhotonCheckBox = QCheckBox("Photonflux")
        self.PhotonEdit = QLineEdit()
        self.PhotonButton = QPushButton("Directory")

        self.ElectronCheckBox = QCheckBox("Electronflux")
        self.ElectronEdit = QLineEdit()
        self.ElectronButton = QPushButton("Directory")

        self.CloseButton = QPushButton("Save and close")


        # +++++++++++ LAYOUT
        frame1Layout=QGridLayout() # how the items within one frame are aligned
        frame1Layout.addWidget(infoLabel,0,0)
        frame1Layout.addWidget(self.OutgassingCheckBox,1,0)
        frame1Layout.addWidget(self.OutgassingEdit,1,1)
        frame1Layout.addWidget(self.OutgassingButton,1,2)

        frame1Layout.addWidget(self.PhotonCheckBox,2,0)
        frame1Layout.addWidget(self.PhotonEdit,2,1)
        frame1Layout.addWidget(self.PhotonButton,2,2)

        frame1Layout.addWidget(self.ElectronCheckBox,3,0)
        frame1Layout.addWidget(self.ElectronEdit,3,1)
        frame1Layout.addWidget(self.ElectronButton,3,2)

        frame1Layout.addWidget(self.CloseButton,4,2)

        self.Frame1.setLayout(frame1Layout)
    
    def initiate_window(self):
        dir= Config.OutgassingFile
        print dir
        if dir != ".":
            parts = Config.OutgassingFile.split('/')
            self.OutgassingEdit.setText(parts[-1])
            self.OutgassingCheckBox.setChecked(True)

        dir= Config.PhotonFile
        if dir != ".":
            parts = Config.PhotonFile.split('/')
            self.PhotonEdit.setText(parts[-1])
            self.PhotonCheckBox.setChecked(True)

        dir= Config.ElectronFile
        if dir != ".":
            parts = Config.ElectronFile.split('/')
            self.ElectronEdit.setText(parts[-1])
            self.ElectronCheckBox.setChecked(True)


    def create_connections(self):
        print('create_connections')
        self.OutgassingCheckBox.stateChanged.connect(self.setOutgassing)
        self.OutgassingEdit.textChanged.connect(self.setOutgassing)
        self.OutgassingButton.clicked.connect(self.openDirectoryOutgassing)

        self.PhotonCheckBox.stateChanged.connect(self.setPhoton)
        self.PhotonEdit.textChanged.connect(self.setPhoton)
        self.PhotonButton.clicked.connect(self.openDirectoryPhoton)

        self.ElectronCheckBox.stateChanged.connect(self.setElectron)
        self.ElectronEdit.textChanged.connect(self.setElectron)
        self.ElectronButton.clicked.connect(self.openDirectoryElectron)

        self.CloseButton.clicked.connect(self.close)
            

    #Functions for connections:
    def openDirectoryOutgassing(self):
        print('openDirectory in property window')
        #print 'test', Config.Config.CrossSection
        dir = (os.path.dirname(Config.DataFolder+'Input/'))# if self.filename is not None else Config.DataFolder+'Input/')
        fname = unicode(QFileDialog.getOpenFileName(self,"IdaVac - Choose CSV-file to upload data", dir))

        #parts=fname.split('/')
        #self.OutgassingEdit.setText(parts[-1])
        self.OutgassingEdit.setText(fname)
        Config.OutgassingFile = fname
        self.OutgassingCheckBox.setChecked(True)

    def setOutgassing(self):
        if self.OutgassingCheckBox.isChecked(): Config.OutgassingFile = self.OutgassingEdit.text()
        else: Config.OutgassingFile = "."

    def openDirectoryPhoton(self):
        dir = (os.path.dirname(Config.DataFolder+'Input/'))
        fname = unicode(QFileDialog.getOpenFileName(self,"IdaVac - Choose CSV-file to upload data", dir))
        parts=fname.split('/')
        self.PhotonEdit.setText(parts[-1])
        Config.PhotonFile = str(fname)
        self.PhotonCheckBox.setChecked(True)

    def setPhoton(self):
        pass
        #if self.PhotonCheckBox.isChecked(): Config.PhotonFile = self.PhotonEdit.text()
        #else: Config.PhotonFile = "."

    def openDirectoryElectron(self):
        dir = (os.path.dirname(Config.DataFolder+'Input/'))
        fname = unicode(QFileDialog.getOpenFileName(self,"IdaVac - Choose CSV-file to upload data", dir))
        parts=fname.split('/')
        self.ElectronEdit.setText(parts[-1])
        Config.ElectronFile = fname
        self.ElectronCheckBox.setChecked(True)

    def setElectron(self):
        pass
        #if self.ElectronCheckBox.isChecked(): Config.ElectronFile = self.ElectronEdit.text()
        #else: Config.ElectronFile = "."

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ExDataWindow()
    ex.show()
    app.exec_()

