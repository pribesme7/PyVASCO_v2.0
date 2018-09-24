import os
import platform
import sys
import Analysis
import PressureRiseDifferentSEY
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


class AnalysisWindow(QMainWindow):
    """
    'Analysis' Window launched by the action 'Analysis' in the menu 'Analysis' of PyVASCO.
    """
    def __init__(self, parent=None):
        super(AnalysisWindow, self).__init__(parent)
        self.tabWidget = QTabWidget()
        self.create_widgets()
        self.setCentralWidget(self.tabWidget)
        self.create_connections()
        self.setWindowTitle("Analysis")


    def create_widgets(self):
        """
       Calls the methods 'create_tab4()', 'create_tab5()' and 'create_tab7()' .
       """
        self.create_tab4()
        self.create_tab5()
        self.create_tab7()


    def create_tab4(self):
        """
        Place and initialize all the widgets in Tab 4, labeled 'Analysis Configuration',  of PyVASCO.
       @return: None
       """
        tab4Widget=QWidget()

        Frame1=QGroupBox("Upload Results in csv.format")
        Frame2=QGroupBox("Sensitivity Analysis")
        Frame3=QGroupBox("Start Simulation")

        #widgets for FRAME 1
        infoLabel = QLabel("Upload data from csv. file: ")
        self.upload1DirectoryLabel = QLabel()
        self.upload1DirectoryButton = QPushButton("Directory to: Upload1")
        self.formatLabel = QLabel("format: ")
        self.formatComboBox = QComboBox()
        self.formatComboBox.setFont(QFont('Verdana'))
        self.formatComboBox.addItems(['x  | y\u2081 | y\u2082 | y\u2083 | y\u2084',' x\u2081 | y\u2081 | x\u2082 | y\u2082 | x\u2083 | y\u2083 | x\u2084 | y\u2084'])
        self.unitLabel = QLabel("unit: ")
        self.unitComboBox = QComboBox()
        self.unitComboBox.addItems(["density -> density", "density -> mbar", "mbar -> mbar", "mbar -> density", "torr -> mbar"])


        self.Plot1_All_CheckBox = QCheckBox("Total of selected.")
        self.Plot1CheckBox = QCheckBox("y\u2081")
        self.Plot1CheckBox.setFont(QFont('Verdana'))
        self.Plot1CheckBox.click()
        self.Plot2CheckBox = QCheckBox(" y\u2082")
        self.Plot2CheckBox.setFont(QFont('Verdana'))
        self.Plot2CheckBox.click()
        self.Plot3CheckBox = QCheckBox(" y\u2083")
        self.Plot3CheckBox.setFont(QFont('Verdana'))
        self.Plot3CheckBox.click()
        self.Plot4CheckBox = QCheckBox(" y\u2084")
        self.Plot4CheckBox.setFont(QFont('Verdana'))
        self.Plot4CheckBox.click()

        self.upload2DirectoryLabel = QLabel()
        self.upload2DirectoryButton = QPushButton("Directory to: Upload2")
        self.format2Label = QLabel("format: ")
        self.format2ComboBox = QComboBox()
        self.format2ComboBox.setFont(QFont('Verdana'))
        self.format2ComboBox.addItems(['x | y\u2081 | y\u2082 | y\u2083 | y\u2084',' x\u2081 | y\u2081 | x\u2082 | y\u2082 | x\u2083 | y\u2083 | x\u2084 | y\u2084'])
        self.unit2Label = QLabel("unit: ")
        self.unit2ComboBox = QComboBox()
        self.unit2ComboBox.addItems(["density -> density", "density -> mbar", "mbar -> mbar", "mbar -> density", "torr -> mbar"])

        self.Plot5_All_CheckBox = QCheckBox("Total of selected.")
        self.Plot5CheckBox = QCheckBox("y\u2081")
        self.Plot5CheckBox.setFont(QFont('Verdana'))
        self.Plot5CheckBox.click()
        self.Plot6CheckBox = QCheckBox(" y\u2082")
        self.Plot6CheckBox.setFont(QFont('Verdana'))
        self.Plot6CheckBox.click()
        self.Plot7CheckBox = QCheckBox(" y\u2083")
        self.Plot7CheckBox.setFont(QFont('Verdana'))
        self.Plot7CheckBox.click()
        self.Plot8CheckBox = QCheckBox(" y\u2084")
        self.Plot8CheckBox.setFont(QFont('Verdana'))
        self.Plot8CheckBox.click()


        #widgets for FRAME 2
        self.logAnalysisCheckBox = QCheckBox("logarithmic scale")
        self.logAnalysisCheckBox.setChecked(True)

        #widgets for FRAME 3
        self.runAnalysisButton = QPushButton("Run Analysis")


        # +++++++++++ LAYOUT
        tab4Layout=QVBoxLayout() # how the frames are aligned

        frame1Layout=QGridLayout() # how the items within one frame are aligned
        frame1Layout.addWidget(infoLabel,0,0)
        frame1Layout.addWidget(self.upload1DirectoryButton,1,0)
        frame1Layout.addWidget(self.upload1DirectoryLabel,1,1)
        frame1Layout.addWidget(self.formatLabel,2,1)
        frame1Layout.addWidget(self.formatComboBox,2,2)
        frame1Layout.addWidget(self.unitLabel,3,1)
        frame1Layout.addWidget(self.unitComboBox,3,2)
        frame1Layout.addWidget(self.Plot1_All_CheckBox,1,3)
        frame1Layout.addWidget(self.Plot1CheckBox,2,3)
        frame1Layout.addWidget(self.Plot2CheckBox,2,4)
        frame1Layout.addWidget(self.Plot3CheckBox,2,5)
        frame1Layout.addWidget(self.Plot4CheckBox,2,6)



        frame1Layout.addWidget(self.upload2DirectoryButton,4,0)
        frame1Layout.addWidget(self.upload2DirectoryLabel,4,1)
        frame1Layout.addWidget(self.format2Label,5,1)
        frame1Layout.addWidget(self.format2ComboBox,5,2)
        frame1Layout.addWidget(self.unit2Label,6,1)
        frame1Layout.addWidget(self.unit2ComboBox,6,2)
        frame1Layout.addWidget(self.Plot5_All_CheckBox,4,3)
        frame1Layout.addWidget(self.Plot5CheckBox,5,3)
        frame1Layout.addWidget(self.Plot6CheckBox,5,4)
        frame1Layout.addWidget(self.Plot7CheckBox,5,5)
        frame1Layout.addWidget(self.Plot8CheckBox,5,6)


        Frame1.setLayout(frame1Layout)

        #FRAME 2
        frame2Layout=QGridLayout() # how the items within one frame are aligned
        frame2Layout.addWidget(self.logAnalysisCheckBox,0,0)
        Frame2.setLayout(frame2Layout)


        frame3Layout=QGridLayout()
        frame3Layout.addWidget(self.runAnalysisButton,0,0)
        Frame3.setLayout(frame3Layout)



        tab4Layout.addWidget(Frame1)
        tab4Layout.addWidget(Frame2)
        tab4Layout.addWidget(Frame3)



        tab4Widget.setLayout(tab4Layout)
        self.tabWidget.addTab(tab4Widget, "Analysis Configuration")


    def create_tab5(self):
        """
        Place and initialize all the widgets in Tab 4, labeled 'Analysis and Comparison',  of PyVASCO.
        @return: None
        """
        tab5Widget=QWidget()

        view = QWidget()
        l = QVBoxLayout()
        view.setLayout(l)
        labelStyle = {'color': '#FFF', 'font-size': '14pt' , 'height': '10pt'}
        b = QFont()
        b.setPixelSize(16)
        self.AnalysisPlotWidget=pg.PlotWidget(name='Comparison: MolFlow and IdaVac')
        self.AnalysisPlotWidget.getPlotItem().getAxis("left").setWidth(90)
        self.AnalysisPlotWidget.getPlotItem().getAxis("left").setStyle(tickTextOffset=16)
        self.AnalysisPlotWidget.getAxis('left').tickFont=b
        self.AnalysisPlotWidget.getPlotItem().getAxis("bottom").setStyle(tickTextOffset=16)
        self.AnalysisPlotWidget.getPlotItem().getAxis('bottom').tickFont=b
        self.AnalysisPlotWidget.setLabel('left', "Pressure (mbar)", **labelStyle)
        self.AnalysisPlotWidget.setLabel('bottom', "Axis alongbeam line (m)", **labelStyle)
        self.AnalysisPlotWidget.showGrid(True, True, 0.5)

        self.logAnalysis()

        self.AnalysisPlotWidget.addLegend()

        l.addWidget(self.AnalysisPlotWidget)

        width_Analysis = 3

        self.Plot1 = self.AnalysisPlotWidget.plot(pen= pg.mkPen(color=Config.ColorPalette['ColorH2'],  width=width_Analysis), name = 'Upload1: Plot1')
        self.Plot2 = self.AnalysisPlotWidget.plot(pen= pg.mkPen(color=Config.ColorPalette['ColorCH4'],  width=width_Analysis), name = 'Upload1: Plot2')
        self.Plot3 = self.AnalysisPlotWidget.plot(pen= pg.mkPen(color=Config.ColorPalette['ColorCO'],  width=width_Analysis), name = 'Upload1: Plot3')
        self.Plot4 = self.AnalysisPlotWidget.plot(pen= pg.mkPen(color=Config.ColorPalette['ColorCO2'],  width=width_Analysis), name = 'Upload1: Plot4')



        self.Plot5 = self.AnalysisPlotWidget.plot(pen= pg.mkPen(color=Config.ColorPalette['ColorH2'],  width=width_Analysis, style=Qt.DotLine), name = 'Upload2: Plot1')
        self.Plot6 = self.AnalysisPlotWidget.plot(pen= pg.mkPen(color=Config.ColorPalette['ColorCH4'],  width=width_Analysis, style=Qt.DotLine), name = 'Upload2: Plot2')
        self.Plot7 = self.AnalysisPlotWidget.plot(pen= pg.mkPen(color=Config.ColorPalette['ColorCO'],  width=width_Analysis, style=Qt.DotLine), name = 'Upload2: Plot3')
        self.Plot8 = self.AnalysisPlotWidget.plot(pen= pg.mkPen(color=Config.ColorPalette['ColorCO2'],  width=width_Analysis, style=Qt.DotLine), name = 'Upload2: Plot4')
        self.Plot1_total = self.AnalysisPlotWidget.plot(pen= pg.mkPen(color=Config.ColorPalette['LightGray'],  width=width_Analysis), name = 'Total1')
        self.Plot5_total = self.AnalysisPlotWidget.plot(pen= pg.mkPen(color=Config.ColorPalette['Gray'],  width=width_Analysis), name = 'Total2')

        tab5Layout=QVBoxLayout()
        tab5Layout.addWidget(view)
        tab5Widget.setLayout(tab5Layout)
        self.tabWidget.addTab(tab5Widget, "Analysis and Comparison")

    def create_tab7(self):
        """
        Place and initialize all the widgets in Tab 4, labeled 'TDIS',  of PyVASCO.
        @return: None
        """
        # TDIS
        tab7Widget = QWidget()


        # FRAMES :
        Frame1 = QGroupBox("TDIS simulation parameters")
        Frame2 = QGroupBox("Results")

        #  Widgets for Frame1: Simulation menu


        self.TDISBeamCurrentLabel = QLabel("Beam Current [A] :")
        self.TDISBeamCurrentEdit = QLineEdit("0.5")

        self.TDISUseTotalQCheckBox = QCheckBox("Use total outgassing for TDIS tanks")
        self.TDISPushButton = QPushButton("Run Simulation")

        # Widgets for Frame2: Plot
        self.TDISPlotWidget = pg.PlotWidget(title='Maximum Pressure Raise ')
        self.TDISPlotWidget.setLogMode(False, True)
        labelStyle = {'color': '#FFF', 'font-size': '14pt'}
        b = QFont()
        b.setPixelSize(16)

        self.TDISPlotWidget = pg.PlotWidget(title='TDIS-Plot', )
        self.TDISPlotWidget.setLabel('left', "Maximum pressure raise", units='mbar', **labelStyle)
        self.TDISPlotWidget.setLabel('bottom', "Half-Gap", units='mm', **labelStyle)
        self.TDISPlotWidget.getPlotItem().getAxis('bottom').setStyle(tickTextOffset=16)
        self.TDISPlotWidget.getPlotItem().getAxis('bottom').tickFont = b
        self.TDISPlotWidget.getPlotItem().getAxis("left").enableAutoSIPrefix(enable=False)
        self.TDISPlotWidget.getPlotItem().getAxis("bottom").enableAutoSIPrefix(enable=False)
        self.TDISPlotWidget.getPlotItem().getAxis('left').setStyle(tickTextOffset=16)
        self.TDISPlotWidget.getPlotItem().getAxis('left').tickFont = b



        self.TDISLegend = self.TDISPlotWidget.addLegend()
        self.TDISPlotWidget.showGrid(True, True, 0.5)

        self.plotTDIS1 = self.TDISPlotWidget.plot(pen=Config.ColorPalette['ColorH2'])
        self.plotTDIS2 = self.TDISPlotWidget.plot(pen=Config.ColorPalette['ColorCH4'])
        self.plotTDIS3 = self.TDISPlotWidget.plot(pen=Config.ColorPalette['ColorCO'])
        self.plotTDIS4 = self.TDISPlotWidget.plot(pen=Config.ColorPalette['ColorCO2'])
        self.plotTDIS5 = self.TDISPlotWidget.plot(pen=Config.ColorPalette['Colortotal'])
        self.plotTDIS6 = self.TDISPlotWidget.plot(pen=Config.ColorPalette['BlueA'])

        # +++++++++++ LAYOUT
        tab7Layout = QVBoxLayout()

        # Frame 1
        frame1Layout = QGridLayout()  # how the items within one frame are aligned


        frame1Layout.addWidget(self.TDISBeamCurrentLabel, 0, 0)
        frame1Layout.addWidget(self.TDISBeamCurrentEdit, 0, 1)

        frame1Layout.addWidget(self.TDISPushButton, 1, 0,1,2)

        Frame1.setLayout(frame1Layout)

        # Frame 2
        frame2Layout = QGridLayout()
        frame2Layout.addWidget(self.TDISPlotWidget, 0, 0)

        Frame2.setLayout(frame2Layout)

        tab7Layout.addWidget(Frame1)
        tab7Layout.addWidget(Frame2)

        tab7Widget.setLayout(tab7Layout)

        self.tabWidget.addTab(tab7Widget, "TDIS")

    def create_connections(self):
        """
        Creates the connections between the GUI widgets and the callback functions.
        """

        print('create_connections')
        # tab4:
        self.upload1DirectoryButton.clicked.connect(self.upload1Directory)
        self.upload2DirectoryButton.clicked.connect(self.upload2Directory)
        self.logAnalysisCheckBox.clicked.connect(self.logAnalysis)
        self.runAnalysisButton.clicked.connect(self.ClickrunAnalysis)

        # Tab7:


        self.TDISPushButton.clicked.connect(self.runTDISSimulation)

    def logAnalysis(self):
        """
         Sets logarithmic scale in the results plot of tab 'Analysis and Comparison'.
        """
        if self.logAnalysisCheckBox.isChecked():
            log = True
        else: log = False
        self.AnalysisPlotWidget.setLogMode(False, log)

    def upload1Directory(self):
        """

        """
        print('uploadDirectory1')
        dir = (os.path.dirname(Config.DataFolder + 'Output/'))
        fname = unicode(QFileDialog.getOpenFileName(self, "IdaVac - Choose CSV-file", dir))
        parts = fname.split('/')
        self.upload1DirectoryLabel.setText(parts[-1])
        Config.Upload1 = fname

    def upload2Directory(self):
        """

        """
        print('uploadDirectory2')
        dir = (os.path.dirname(Config.DataFolder + 'Output/'))
        fname = unicode(QFileDialog.getOpenFileName(self, "IdaVac - Choose CSV-file", dir))
        parts = fname.split('/')
        self.upload2DirectoryLabel.setText(parts[-1])
        Config.Upload2 = fname

    def ClickrunAnalysis(self):
        """
        When clicked, changes the text of the button 'Run Simulation' in Tab 'Data' to 'Running' and raises a warning
        message in case of unsuccessful simulation.
        @return: None
        """
        self.runAnalysisButton.setText('Runnning...')
        flag = Analysis.runAnalysis(self, Config.Upload1, Config.Upload2)
        if flag == False:
            QMessageBox.warning(self, "Unsuccessful!", "Unsuccessful Analysis: Please check your input format!",
                                QMessageBox.Ok)
        self.runAnalysisButton.setText('Run Analysis')

    def runTDISSimulation(self):
        """
        Runs the simulation on the TDIS and plots the result in the tab 'TDIS'. See the user manual for more details.
        @return: None
        """
        try:
            Current = float(self.TDISBeamCurrentEdit.text())
        except:
            QMessageBox.warning(self, "Invalid value for Beam Current", "Beam Current must be a number!", QMessageBox.Ok)

        halfGapRange, data = PressureRiseDifferentSEY.runTDISSimulation_nonHomogeneousSEY(Current)
        self.TDISPlot(halfGapRange, data)


    def TDISPlot(self,halfGapRange, data):
        """
        Plots the result of the TDIS Simulation. \n
        Parameters:
        -----------
        @param  halfGapRange: (list) : List of Half-Geps considered in the simulation. See the user manual for more details.
        @param  data: Maximum pressure as a function of the Half-Gap for different simulated SEY. See the user manual for more details.
        @return:
        """
        print("TDIS plot")
        try:
            print(self.names)
            for t in self.names:
                self.critLegend.removeItem(t)
            self.names = []
            self.plotTDIS1.setData(x=[], y=[])
            self.plotTDIS2.setData(x=[], y=[])
            self.plotTDIS3.setData(x=[], y=[])
            self.plotTDIS4.setData(x=[], y=[])
            self.plotTDIS5.setData(x=[], y=[])
        except:
            self.names = []

        n = len(data.keys()) - 1
        keys = data.keys()
        print( "SEY values",keys)
        self.plotTDIS1.setData(x=halfGapRange,y=data[keys[0]])
        self.TDISLegend.addItem(self.plotTDIS1, name= str(keys[0]))
        self.names.append(str(keys[0]))

        self.plotTDIS2.setData(x=halfGapRange, y=data[keys[1]])
        self.TDISLegend.addItem(self.plotTDIS2, name= str(keys[1]))
        self.names.append(str(keys[1]))

        self.plotTDIS3.setData(x=halfGapRange, y=data[keys[2]])
        self.TDISLegend.addItem(self.plotTDIS3, name= str(keys[2]))
        self.names.append("SEY " + str(keys[2]))

        self.plotTDIS4.setData(x=halfGapRange, y=data[keys[3]])
        self.TDISLegend.addItem(self.plotTDIS4, name= str(keys[3]))
        self.names.append("SEY " + str(keys[3]))

        self.plotTDIS5.setData(x=halfGapRange, y=data[keys[4]])
        self.TDISLegend.addItem(self.plotTDIS5, name= str(keys[4]))
        self.names.append(str(keys[4]))





if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = AnalysisWindow()
    ex.show()
    app.exec_()


