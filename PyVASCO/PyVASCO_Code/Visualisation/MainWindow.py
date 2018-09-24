#!/usr/bin/env python
# Copyright (c) 2008-14 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future_builtins import *
from datetime import datetime
from pytz import timezone

import os
import platform
import sys
import numpy as np

import PropertyWindow
#import ExternalDataWindow
import Scrubbing

import NewMaterialWindow,NewPumpWindow,NewGasSourceWindow,NewESDcurve,NewInput,AnalysisWindow,ShowWindow
import MySimulationsWindow, CryoWindow


from PyQt4.QtCore import (PYQT_VERSION_STR, QFile, QFileInfo, QSettings,
        QString, QT_VERSION_STR, QTimer, QVariant, Qt,QDir, QReadLocker, QReadWriteLock, QRectF)
from PyQt4.QtCore import pyqtSignal as Signal
from PyQt4.QtGui import *
from . import ScientificDoubleSpinBox
import pyqtgraph as pg #built on PYQT4 / PySide and numpy
import pyqtgraph.opengl as gl
from Components.ESD import ESD
import webbrowser


from Computation import dataDensity
from Config import Config
from Computation.dataDensity import Density 
#from dataDensity import Density
from Computation.Core2 import Calculate, GetSegments, SetPumpingSpeedforAvgPressure
#from InputTransform import Main_Material_Transformation
from InputFormat.InputTransform import Main_Material_Transformation


__version__ = "2.0.0"



  
class Window(QMainWindow):
    """
    Main window of PyVASCO. Inheritates from QMainWindow
    """
    oldFormatFilePath=''
    filePath=''

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.tabWidget=QTabWidget()
        self.dirty = False
        self.filename = Config.DataFile #QDir.homePath() #None
        self.create_widgets()
        self.create_actions()
        self.create_menu()
        self.initiateMainWindow()
        self.create_connections()
        self.setWindowTitle("PyVASCO")
        self.nameEdit.selectAll()
        self.nameEdit.setFocus()
        self.setCentralWidget(self.tabWidget)
        self.center()

    def create_menu(self):
        """
        Creates main menu.
        """
        self.menuBar= QMenu("TextEffect")


    def create_tab1(self):
        """
        Place and initialize all the widgets in Tab 1, labeled 'Data', of PyVASCO.
        """
        tab1Widget=QWidget()

        Frame1=QGroupBox("Load Data")
        Frame2=QGroupBox("Plot properties")
        Frame3=QGroupBox("Simulation parameters")
        Frame4=QGroupBox("Beam parameters and critical current")
        Frame5=QGroupBox("Start Simulation")

        #widgets for FRAME 1 
        nameLabel = QLabel("Name of Simulation")
        self.nameEdit = QLineEdit("")
        self.transformButton = QPushButton("Transform...")
        self.transformDirectoryButton = QPushButton("Open Directory: Input file_Old ")
        self.transformEdit = QLineEdit()
        self.uploadButton = QPushButton("Open Directory: Input file_New")
        self.uploadEdit = QLineEdit()
        self.saveButton = QPushButton("Save results in folder")
        self.saveEdit = QLineEdit()
        self.gaugesButton = QPushButton("Gauges value")
        self.gaugesEdit = QLineEdit()
        self.gaugesSpinbox = QDoubleSpinBox(value=0, singleStep=0.1, minimum = -100000., maximum = 100000. )
        self.savetxtCheckBox = QCheckBox("Save simulation values in csv-file")
        self.ThreeDCheckBox = QCheckBox("Print 3D sketch of the domain")


        #widgets for FRAME 2 

        plottingLabel = QLabel("Plotting Quality")
        self.plottingSlider = QSlider(Qt.Horizontal, value=10)
        self.logCheckBox = QCheckBox("Logarithmic Scale")
        shiftLabel = QLabel("Shift x-axis [m]")
        self.shiftEdit = QLineEdit()

        #widgets for FRAME 3

        specieLabel = QLabel("Choose gas species:")

        self.allgasCheckBox = QCheckBox("Select all gas species")
        self.h2CheckBox = QCheckBox("H2")
        self.ch4CheckBox = QCheckBox("CH4")
        self.coCheckBox = QCheckBox("CO")
        self.co2CheckBox = QCheckBox("CO2")
        self.totalCheckBox = QCheckBox("Total of all gas species")
        self.UseRecursivePumpingSpeedCheckButton = QCheckBox("Pumping Speed depending on the pressure")


        massLabel = QLabel("Molecular weight: ") #nist.gov
        self.massEdit1 = QLineEdit("2.01588")
        self.massEdit2 = QLineEdit("16.0425")
        self.massEdit3 = QLineEdit("28.0101")
        self.massEdit4 = QLineEdit("44.0095")

        crossSectionLabel = QLabel("Ionization cross section: ")
        self.crossSectionEdit1 = QLineEdit("4.45E-23")
        self.crossSectionEdit2 = QLineEdit("3.18E-22")
        self.crossSectionEdit3 = QLineEdit("2.75E-22")
        self.crossSectionEdit4 = QLineEdit("4.29E-22")
        sensitivityLabel = QLabel("Sensitivityfactor:")

        self.densityRadioButton = QRadioButton("Density")
        self.pressureRadioButton = QRadioButton("Pressure")
        self.h2SpinBox = QDoubleSpinBox(value=0.416666, singleStep=0.05, minimum=0.1)
        self.ch4SpinBox = QDoubleSpinBox(value=1.4285, singleStep=0.05, minimum=0.1)
        self.coSpinBox = QDoubleSpinBox(value=1.1111, singleStep=0.05, minimum=0.1)
        self.co2SpinBox = QDoubleSpinBox(value=1.4285, singleStep=0.05, minimum=0.1)




        #widgets for FRAME 4
        currentLabel = QLabel("Beam Current [A]")
        self.currentEdit = QLineEdit("0.5")
        self.currentCheckBox = QCheckBox("Compute critical current")

        initialcurrentLabel = QLabel("Initial current [A]")
        self.initialcurrentSpinBox = QDoubleSpinBox(value=1.0, singleStep=0.1, minimum=0.1)

        precisioncurrentLabel = QLabel("Precission [A]")
        self.precisioncurrentSpinBox = QDoubleSpinBox(value=0.1, singleStep=0.1, minimum=0.1)

        stepscurrentLabel = QLabel("calculation steps")
        self.stepscurrentSpinBox = QSpinBox(value=10)

        #widgets for FRAME 5
        self.runsimulationButton = QPushButton("Run Simulation")






        # +++++++++++ LAYOUT
        tab1Layout=QVBoxLayout() # how the frames are aligned

        frame1Layout=QGridLayout() # how the items within one frame are aligned
        frame1Layout.addWidget(nameLabel,0,0)
        frame1Layout.addWidget(self.nameEdit,0,1)
        frame1Layout.addWidget(self.transformDirectoryButton,1,0)
        frame1Layout.addWidget(self.transformEdit,1,1)
        frame1Layout.addWidget(self.transformButton,1,2)

        frame1Layout.addWidget(self.uploadButton,2,0)
        frame1Layout.addWidget(self.uploadEdit,2,1)
        frame1Layout.addWidget(self.saveButton,3,0)
        frame1Layout.addWidget(self.saveEdit,3,1)
        frame1Layout.addWidget(self.gaugesButton,4,0)
        frame1Layout.addWidget(self.gaugesEdit,4,1)
        frame1Layout.addWidget(self.gaugesSpinbox,4,2)

        frame1Layout.addWidget(self.savetxtCheckBox,5,0)
        frame1Layout.addWidget(self.ThreeDCheckBox,6,0)

        Frame1.setLayout(frame1Layout)


        frame2Layout=QGridLayout()







        frame2Layout.addWidget(plottingLabel,0,0)
        frame2Layout.addWidget(self.plottingSlider,0,1,1,4)
        frame2Layout.addWidget(self.logCheckBox,1,0)
        frame2Layout.addWidget(QLabel("                    "), 1, 1, 1, 2)
        frame2Layout.addWidget(shiftLabel, 1, 3)
        frame2Layout.addWidget(self.shiftEdit, 1, 4)
        Frame2.setLayout(frame2Layout)




        frame3Layout=QGridLayout()

        frame3Layout.addWidget(self.densityRadioButton,1,0)
        frame3Layout.addWidget(self.pressureRadioButton,1,1)
        frame3Layout.addWidget(specieLabel,2,0)
        frame3Layout.addWidget(self.allgasCheckBox,3,0)
        frame3Layout.addWidget(massLabel,3,1)
        frame3Layout.addWidget(crossSectionLabel,3,2)

        frame3Layout.addWidget(sensitivityLabel,3,3)

        frame3Layout.addWidget(self.massEdit1,4,1)
        frame3Layout.addWidget(self.massEdit2,5,1)
        frame3Layout.addWidget(self.massEdit3,6,1)
        frame3Layout.addWidget(self.massEdit4,7,1)


        frame3Layout.addWidget(self.crossSectionEdit1,4,2)
        frame3Layout.addWidget(self.crossSectionEdit2,5,2)
        frame3Layout.addWidget(self.crossSectionEdit3,6,2)
        frame3Layout.addWidget(self.crossSectionEdit4,7,2)

        frame3Layout.addWidget(self.h2CheckBox,4,0)
        frame3Layout.addWidget(self.h2SpinBox,4,3)
        frame3Layout.addWidget(self.ch4CheckBox,5,0)
        frame3Layout.addWidget(self.ch4SpinBox,5,3)
        frame3Layout.addWidget(self.coCheckBox,6,0)
        frame3Layout.addWidget(self.coSpinBox,6,3)
        frame3Layout.addWidget(self.co2CheckBox,7,0)
        frame3Layout.addWidget(self.co2SpinBox,7,3)
        frame3Layout.addWidget(self.totalCheckBox,8,0)
        frame3Layout.addWidget(self.UseRecursivePumpingSpeedCheckButton,8,2)

        Frame3.setLayout(frame3Layout)



        frame4Layout=QGridLayout()

        frame4Layout.addWidget(currentLabel, 0, 0)
        frame4Layout.addWidget(self.currentEdit, 0, 1)
        frame4Layout.addWidget(self.currentCheckBox,1,0,1,2)

        frame4Layout.addWidget(initialcurrentLabel,1,2)
        frame4Layout.addWidget(self.initialcurrentSpinBox,1,3)

        frame4Layout.addWidget(precisioncurrentLabel, 1, 4)
        frame4Layout.addWidget(self.precisioncurrentSpinBox, 1, 5)

        frame4Layout.addWidget(stepscurrentLabel,1,6)
        frame4Layout.addWidget(self.stepscurrentSpinBox,1,7)

        Frame4.setLayout(frame4Layout)

        frame5Layout=QGridLayout()
        frame5Layout.addWidget(self.runsimulationButton,0,0)
        Frame5.setLayout(frame5Layout)
        Frame5.setFixedHeight(75)




        tab1Layout.addWidget(Frame1)
        tab1Layout.addWidget(Frame2)
        tab1Layout.addWidget(Frame3)
        tab1Layout.addWidget(Frame4)
        tab1Layout.addWidget(Frame5)




        tab1Widget.setLayout(tab1Layout)
        self.tabWidget.addTab(tab1Widget, "Data")




    def create_tab2(self):
        """
        Place and initialize all the widgets in Tab 2, labeled 'Simulation',  of PyVASCO.
        @return:  None
        """
        tab2Widget=QWidget()

        #item
        view = QWidget()
        self.l = QVBoxLayout()
        view.setLayout(self.l)
        labelStyle = {'color': '#FFF', 'font-size': '14pt'}


        font = QFont()
        font.setPixelSize(16)
        self.densityPlotWidget=pg.PlotWidget(title='Density-Plot', )
        self.densityPlotWidget.setLabel('left', "Density", units='molecules/m<sup>3</sup>', **labelStyle)
        self.densityPlotWidget.setLabel('bottom', "Axis along beam line", units='m', **labelStyle)
        self.densityPlotWidget.getPlotItem().getAxis("left").enableAutoSIPrefix(enable=False)
        self.densityPlotWidget.addLegend()
        self.densityPlotWidget.showGrid(True, True, 0.5)
        self.densityPlotWidget.getPlotItem().getAxis("left").setStyle(tickTextOffset=16)
        self.densityPlotWidget.getPlotItem().getAxis("left").setWidth(120)
        self.densityPlotWidget.getPlotItem().getAxis("left").tickFont = font
        self.densityPlotWidget.getPlotItem().getAxis("bottom").setStyle(tickTextOffset=16)
        self.densityPlotWidget.getPlotItem().getAxis("bottom").tickFont = font

        self.geometryPlotWidget=pg.PlotWidget(title='Geometry',**labelStyle)
        self.geometryPlotWidget.setLabel('left', "Diameter", units='m', **labelStyle)
        self.geometryPlotWidget.setLabel('bottom', "Axis along beam line", units='m', **labelStyle)
        self.geometryPlotWidget.getPlotItem().getAxis("left").setStyle(tickTextOffset=16)
        self.geometryPlotWidget.getPlotItem().getAxis("left").setWidth(120)
        self.geometryPlotWidget.getPlotItem().getAxis("left").tickFont = font
        self.geometryPlotWidget.getPlotItem().getAxis("bottom").setStyle(tickTextOffset=16)
        self.geometryPlotWidget.getPlotItem().getAxis("bottom").tickFont = font

        self.l.addWidget(self.densityPlotWidget)
        self.l.addWidget(self.geometryPlotWidget)
        self.geometryPlotWidget.setXLink(self.densityPlotWidget)
        self.geometryPlotWidget.showGrid(True, True, 0.5)

        width_gas = 1.5
        width_total = 2

        self.plotH2 = self.densityPlotWidget.plot(pen = pg.mkPen(color=Config.ColorPalette['ColorH2'], width=width_gas), name = 'H<sub>2</sub>')
        self.plotCH4 = self.densityPlotWidget.plot(pen = pg.mkPen(color=Config.ColorPalette['ColorCH4'], width=width_gas), name = 'CH<sub>4</sub>')
        self.plotCO = self.densityPlotWidget.plot(pen = pg.mkPen(color=Config.ColorPalette['ColorCO'], width=width_gas), name = 'CO')
        self.plotCO2 = self.densityPlotWidget.plot(pen = pg.mkPen(color=Config.ColorPalette['ColorCO2'], width=width_gas), name = 'CO<sub>2</sub>')
        self.plot_total = self.densityPlotWidget.plot(pen = pg.mkPen(color=Config.ColorPalette['Colortotal'], width=width_total), name = 'Total pressure')
        self.plot_Data = self.densityPlotWidget.plot(pen= None, symbol = 'o', symbolSize = 5, symbolPen = (255, 255, 255, 200), symbolBrush = (0,0,255,150), name = 'LHC data')
        self.plot_Data_blue = self.densityPlotWidget.plot(pen= None, symbol = '+', symbolSize = 5, symbolPen = (255, 255, 255, 200), symbolBrush = (0,0,255,150), name = 'LHC data')


        tab2Layout=QVBoxLayout()

        tab2Layout.addWidget(self.densityRadioButton)
        tab2Layout.addWidget(self.pressureRadioButton)
        tab2Layout.addWidget(view)
        tab2Widget.setLayout(tab2Layout)
        self.tabWidget.addTab(tab2Widget, "Simulation")

    def create_tab3(self):
        """
        Place and initialize all the widgets in Tab 3, labeled 'Critical Current', of PyVASCO.
        @return:  None
       """
        self.critCurrentLabel = QLabel("")
        tab3Widget=QWidget()

        view = QWidget()
        l = QVBoxLayout()
        view.setLayout(l)

        critCurrent1PlotWidget=pg.PlotWidget(title='Density profile at different currents')
        critCurrent1PlotWidget.setLogMode(False, True)
        critCurrent1PlotWidget.showGrid(True, True, 0.5)
        critCurrent2PlotWidget=pg.PlotWidget(title='Dynamic Current')
        critCurrent2PlotWidget.showGrid(True, True, 0.5)
        l.addWidget(critCurrent1PlotWidget)
        l.addWidget(critCurrent2PlotWidget)


        labelStyle = {'color': '#FFF', 'font-size': '14pt'}
        critCurrent1PlotWidget.setLabel('left', "Density", units='molecules/m<sup>3</sup>', **labelStyle)
        critCurrent1PlotWidget.setLabel('bottom', "Axis along beam line", units='m', **labelStyle)
        critCurrent2PlotWidget.setLabel('left', "Density", units='molecules/m<sup>3</sup>', **labelStyle)
        critCurrent2PlotWidget.setLabel('bottom', "Current", units='A', **labelStyle)

        critCurrent1PlotWidget.getPlotItem().getAxis("left").enableAutoSIPrefix(enable=False)
        font = QFont()
        font.setPixelSize(16)
        critCurrent1PlotWidget.getPlotItem().getAxis("left").setStyle(tickTextOffset=16)
        critCurrent1PlotWidget.getPlotItem().getAxis("left").setWidth(120)
        critCurrent1PlotWidget.getPlotItem().getAxis("left").tickFont = font
        critCurrent1PlotWidget.getPlotItem().getAxis("bottom").setStyle(tickTextOffset=16)
        critCurrent1PlotWidget.getPlotItem().getAxis("bottom").tickFont = font

        critCurrent2PlotWidget.getPlotItem().getAxis("left").setStyle(tickTextOffset=16)
        critCurrent2PlotWidget.getPlotItem().getAxis("left").setWidth(120)
        critCurrent2PlotWidget.getPlotItem().getAxis("left").tickFont = font
        critCurrent2PlotWidget.getPlotItem().getAxis("bottom").setStyle(tickTextOffset=16)
        critCurrent2PlotWidget.getPlotItem().getAxis("bottom").tickFont = font
        critCurrent2PlotWidget.getPlotItem().getAxis("left").enableAutoSIPrefix(enable=False)
        critCurrent2PlotWidget.addLegend()
        self.critLegend =critCurrent1PlotWidget.addLegend()

        self.plotCurrent1 = critCurrent1PlotWidget.plot(pen=Config.ColorPalette['ColorH2'])
        self.plotCurrent2 = critCurrent1PlotWidget.plot(pen=Config.ColorPalette['ColorCH4'])
        self.plotCurrent3 = critCurrent1PlotWidget.plot(pen=Config.ColorPalette['ColorCO'])
        self.plotCurrent4 = critCurrent1PlotWidget.plot(pen=Config.ColorPalette['ColorCO2'])

        '''
        self.plotCurrent1 = critCurrent1PlotWidget.plot(pen=Config.ColorPalette['ColorH2'], name = 'H<sub>2</sub>')
        self.plotCurrent2 = critCurrent1PlotWidget.plot(pen=Config.ColorPalette['ColorCH4'], name = 'CH<sub>4</sub>')
        self.plotCurrent3 = critCurrent1PlotWidget.plot(pen=Config.ColorPalette['ColorCO'], name = 'CO')
        self.plotCurrent4 = critCurrent1PlotWidget.plot(pen=Config.ColorPalette['ColorCO2'], name = 'CO<sub>2</sub>'')
        '''

        self.CurrentDyn1Plot = critCurrent2PlotWidget.plot(pen=Config.ColorPalette['ColorH2'], name = 'H<sub>2</sub>')
        self.CurrentDyn2Plot = critCurrent2PlotWidget.plot(pen=Config.ColorPalette['ColorCH4'], name = 'CH<sub>4</sub>')
        self.CurrentDyn3Plot = critCurrent2PlotWidget.plot(pen=Config.ColorPalette['ColorCO'], name = 'CO')
        self.CurrentDyn4Plot = critCurrent2PlotWidget.plot(pen=Config.ColorPalette['ColorCO2'], name = 'CO<sub>2</sub>')


        tab3Layout=QVBoxLayout()
        tab3Layout.addWidget(self.critCurrentLabel)
        tab3Layout.addWidget(view)
        tab3Widget.setLayout(tab3Layout)
        self.tabWidget.addTab(tab3Widget, "Critical Current")


    def create_tab6(self):
        """
        Place and initialize all the widgets in Tab 6, labeled 'Scrubbing Simulation',  of PyVASCO.
        @return:  None
        """
        # Study of the Scrubbing effect
        tab6Widget = QWidget()


        # FRAMES :
        Frame1 = QGroupBox("Load data")
        self.Frame2 = QGroupBox("Simulation parameters")
        self.Frame2p = QGroupBox("Simulation parameters")
        Frame3 = QGroupBox("Results")


        #  Widgets for Frame1: Simulation menu
        self.uploadScrubbingButton = QPushButton("Open Directory: Input file_New")
        self.uploadEdit6 = QLineEdit()
        self.OneESDFromEDoseRadioButton = QRadioButton("ESD from accumulated electron dose")
        self.ESDFromScanEDoses = QRadioButton("Scan ESDs for different accumulated electron doses")
        self.OneESDFromEDoseRadioButton.setChecked(True)

        #  Widgets for Frame2: Simulation parameters

        # Frame 2, option 1
        self.esdFromDoseLabel = QLabel("Estimated electron dose [e-/cm^2]")
        self.esdFromDoseSlider = QSlider(Qt.Horizontal, value=6)
        self.esdFromDoseSlider.setMinimum(13)
        self.esdFromDoseSlider.setMaximum(19)
        self.esdFromDoseSlider.setValue(15)
        self.esdFromDoseInfo = QLabel("1e" + str(self.esdFromDoseSlider.value()))
        self.scrubbingOp1PushButton = QPushButton("Start simulation")

        # Frame 2, option 2
        self.scrubbingOp2PushButton = QPushButton("Start simulation")
        self.minElectronDose = ScientificDoubleSpinBox(value=1e14, singleStep=1e14, minimum = 1e13, maximum = 1e15)
        self.maxElectronDose = ScientificDoubleSpinBox(value=5e18, singleStep=1e17, minimum = 1e18, maximum = 1e19)
        self.eDoseSteps = QDoubleSpinBox(value=3, singleStep=1, minimum = 2, maximum = 5)


        self.eDoseSteps.setDecimals(0)


        # Widgets for Frame3: Plot
        self.scrubbingPlotWidget = pg.PlotWidget(title='Pressure profile ')
        self.scrubbingPlotWidget.setLogMode(False, True)
        labelStyle = {'color': '#FFF', 'font-size': '14pt'}
        self.scrubbingPlotWidget= pg.PlotWidget(title='Scrubbing-Plot', )
        self.scrubbingPlotWidget.setLabel('left', "Density", units='molecules/m<sup>3</sup>', **labelStyle)
        self.scrubbingPlotWidget.setLabel('bottom', "Axis along beam line", units='m', **labelStyle)
        self.scrubbingPlotWidget.getPlotItem().getAxis("left").enableAutoSIPrefix(enable=False)
        font = QFont()
        font.setPixelSize(16)
        self.scrubbingPlotWidget.getPlotItem().getAxis("left").setStyle(tickTextOffset= 16)
        self.scrubbingPlotWidget.getPlotItem().getAxis("left").setWidth(120)
        self.scrubbingPlotWidget.getPlotItem().getAxis("left").tickFont= font
        self.scrubbingPlotWidget.getPlotItem().getAxis("bottom").setStyle(tickTextOffset=16)
        self.scrubbingPlotWidget.getPlotItem().getAxis("bottom").tickFont = font
        self.scrubbingPlotWidget.showGrid(True, True, 0.5)



        # +++++++++++ LAYOUT
        tab6Layout = QVBoxLayout()  # how the frames are aligned

        # Frame 1
        frame1Layout = QGridLayout()  # how the items within one frame are aligned
        frame1Layout.addWidget(self.uploadScrubbingButton,0,0)
        frame1Layout.addWidget(self.uploadEdit6,0,1)
        frame1Layout.addWidget(self.OneESDFromEDoseRadioButton,1,0)
        frame1Layout.addWidget(self.ESDFromScanEDoses,1,1)
        Frame1.setLayout(frame1Layout)


        # Frame 2
        # Option 1
        frame2Layout = QGridLayout()

        frame2Layout.addWidget(self.esdFromDoseLabel, 1, 0)
        frame2Layout.addWidget(self.esdFromDoseSlider, 1, 1)
        frame2Layout.addWidget(self.esdFromDoseInfo, 1, 2)
        frame2Layout.addWidget(self.scrubbingOp1PushButton,2,0,1,3)

        self.Frame2.setLayout(frame2Layout)

        # Option 2
        frame2pLayout = QGridLayout()
        frame2pLayout.addWidget(QLabel("Minimum accumulated electron dose [e-/cm^2]"),0,0)
        frame2pLayout.addWidget(self.minElectronDose,0,1)
        frame2pLayout.addWidget(QLabel("Maximum accumulated electron dose [e-/cm^2]"),0,2)
        frame2pLayout.addWidget(self.maxElectronDose, 0, 3)
        frame2pLayout.addWidget(QLabel("Steps"), 0, 4)
        frame2pLayout.addWidget(self.eDoseSteps, 0, 5)

        frame2pLayout.addWidget(self.scrubbingOp2PushButton,1,0,1,6)
        self.Frame2p.setLayout(frame2pLayout)

        # Frame 3
        frame3Layout = QGridLayout()
        frame3Layout.addWidget(self.scrubbingPlotWidget,0,0)
        Frame3.setLayout(frame3Layout)

        tab6Layout.addWidget(Frame1)
        tab6Layout.addWidget(self.Frame2)
        tab6Layout.addWidget(self.Frame2p)
        tab6Layout.addWidget(Frame3)

        self.Frame2p.hide()

        tab6Widget.setLayout(tab6Layout)
        self.tabWidget.addTab(tab6Widget, "Dynamic pressure due to ESD")



    def create_widgets(self):
        """
        Initialize the different tabs of PyVASCO.
        @return:  None
        """
        self.create_tab1()
        self.create_tab2()
        self.create_tab3()
        self.create_tab6()


    def create_connections(self):
        """
        Creates the connections between the GUI widgets and the callback functions.

        """
        print('create_connections')
        self.transformDirectoryButton.clicked.connect(self.oldfileDirectory)
        self.transformButton.clicked.connect(self.transformInput)
        self.uploadButton.clicked.connect(self.fileNew)
        self.saveButton.clicked.connect(self.saveDirectory)
        self.gaugesButton.clicked.connect(self.gaugesUpload)
        self.runsimulationButton.clicked.connect(self.runSimulation)
        self.allgasCheckBox.stateChanged.connect(self.checkallgas)
        self.pressureRadioButton.toggled.connect(self.PressureDensity)
        self.logCheckBox.stateChanged.connect(self.logScale)
        self.plottingSlider.valueChanged.connect(self.PlottingQuality)


        #Visibility of Plot according to checkbox value
        self.h2CheckBox.stateChanged.connect(self.h2Visible)
        self.ch4CheckBox.stateChanged.connect(self.ch4Visible)
        self.coCheckBox.stateChanged.connect(self.coVisible)
        self.co2CheckBox.stateChanged.connect(self.co2Visible)
        self.totalCheckBox.stateChanged.connect(self.totalVisible)

        self.gaugesEdit.textChanged.connect(self.updateLHCData)

        #Sensitivityfactor:
        self.h2SpinBox.valueChanged.connect(self.h2Sensitivity)
        self.ch4SpinBox.valueChanged.connect(self.ch4Sensitivity)
        self.coSpinBox.valueChanged.connect(self.coSensitivity)
        self.co2SpinBox.valueChanged.connect(self.co2Sensitivity)


        #tab6:
        self.uploadScrubbingButton.clicked.connect(self.fileScrubbingNew)
        self.ESDFromScanEDoses.clicked.connect(self.ShowOp2Scrubbing)
        self.OneESDFromEDoseRadioButton.clicked.connect(self.ShowOp1Scrubbing)
        self.scrubbingOp1PushButton.clicked.connect(self.RunScrubbingSimulation)
        self.esdFromDoseSlider.valueChanged.connect(self.setESDFromDose)
        self.scrubbingOp2PushButton.clicked.connect(self.RunScrubbingSimulation2)


    def ShowOp1Scrubbing(self):
        self.Frame2p.hide()
        self.Frame2.show()

    def ShowOp2Scrubbing(self):
        self.Frame2.hide()
        self.Frame2p.show()



    def h2Visible(self):
        """
        Makes the H2 curve visible if the H2 check-button in the tab 'Data' is checked.
        @return:  None
        """
        if self.h2CheckBox.isChecked():
            self.plotH2.setData(x = Density.X,y = Density.H2)
        else: self.plotH2.setData(x = [], y = [])
        self.l.update()

    def ch4Visible(self):
        """
        Makes the CH4 curve visible in the results of tab 'Simulation' if the CH4 check-button in the tab 'Data' is checked.
        @return:  None
        """
        if self.ch4CheckBox.isChecked(): self.plotCH4.setData(x = Density.X, y = Density.CH4)
        else: self.plotCH4.setData(x = [], y = [])
        self.l.update()

    def coVisible(self):
        """
        Makes the CO curve visible in the results of tab 'Simulation' if the CO check-button in the tab 'Data' is checked.
        @return:  None
        """
        if self.coCheckBox.isChecked(): self.plotCO.setData(x = Density.X, y = Density.CO)
        else: self.plotCO.setData(x = [], y = [])
        self.l.update()

    def co2Visible(self):
        """
        Makes the CO2 curve visible in the results of tab 'Simulation' if the CO2 check-button in the tab 'Data' is checked.
        @return:  None
        """
        if self.co2CheckBox.isChecked(): self.plotCO2.setData(x = Density.X, y = Density.CO2)
        else: self.plotCO2.setData(x = [], y = [])
        self.l.update()

    def totalVisible(self):
        """
        Makes the total pressure curve visible in the results of tab 'Simulation' if the 'Total of all gas species' check-button in the tab 'Data' is checked.
        The total pressure is computed according to the values of the sensitivity factors for each specie selected in the 'Data' tab of PyVASCO.
        @return:  None
        """
        if self.totalCheckBox.isChecked() and Density.density is False:
            total_Density = Density.SensitivityTotal()
            item =self.plot_total.setData(x = Density.X, y = total_Density)
            self.densityPlotWidget.plotItem.legend.addItem(item,"Total pressure")
        else: self.plot_total.setData(x = [], y = [])
        self.l.update()

    def h2Sensitivity(self):
        """
        Sets the value for the sensitivity factor of H2 for conversion between molecules density and pressure.
        @return:  None
        """
        Density.SensitivityFactor[0] =  self.h2SpinBox.value()

        #if self.h2CheckBox.isChecked(): self.plotH2.setData(x = Density.X, y = Density.H2)
        #self.l.update()

    def ch4Sensitivity(self):
        """
        Sets the value for the sensitivity factor of CH4 for conversion between molecules density and pressure.
        @return:  None
        """
        Density.SensitivityFactor[1] = self.ch4SpinBox.value()
        #if self.ch4CheckBox.isChecked(): self.plotCH4.setData(x = Density.X, y = Density.CH4)
        #self.l.update()

    def coSensitivity(self):
        """
        Sets the value for the sensitivity factor of CO for conversion between molecules density and pressure.
        @return:  None
        """
        Density.SensitivityFactor[2] = self.coSpinBox.value()
        #if self.coCheckBox.isChecked(): self.plotCO.setData(x = Density.X, y = Density.CO)
        #self.l.update()

    def co2Sensitivity(self):
        """
        Sets the value for the sensitivity factor of CO2 for conversion between molecules density and pressure.
        @return:  None
        """
        Density.SensitivityFactor[3]= self.co2SpinBox.value()
        #if self.co2CheckBox.isChecked(): self.plotCO2.setData(x = Density.X, y = Density.CO2)
        #self.l.update()

    def setESDFromDose(self):
        """
        Sets the ESD (Electron Stimulated Desorption) yield from a set accumulated electron dose. 
        @return:  None
        """
        self.esdFromDoseInfo.setText('1.0e' + str(self.esdFromDoseSlider.value()))
        self.eDose = float('1.0e' + str(self.esdFromDoseSlider.value()))


    def getESDFromDose(self):
        """
        Gets the ESD of a certain material given an approximated electron dose
        @return:  None
        """
        #newESD = ESD(self.eDose)
        try:
            Config.eDose = self.eDose
        except:
            Config.eDose = 1e15
        Config.UpdateESD = True
        Config.useESDCurve = True

    '''
    def ClickrunAnalysis(self):
        """
        When clicked, changes the text of the button 'Run Simulation' in Tab 'Data' to 'Running' and raises a warning
        message in case of unsuccessful simulation.
        @return:  None
        """
        self.runAnalysisButton.setText('Runnning...')
        flag = Analysis.runAnalysis(self, Config.Upload1, Config.Upload2)
        if flag == False:
            QMessageBox.warning(self, "Unsuccessful!", "Unsuccessful Analysis: Please check your input format!", QMessageBox.Ok)
        self.runAnalysisButton.setText('Run Analysis')
    '''


    def RunScrubbingSimulation2(self):
        """
        Runs the simulation on the Scrubbing effect and plots the result in the tab 'Scrubbing Simulation'. See the user manual for more details.
        @return:  None

        """

        self.scrubbingOp1PushButton.setText("Running...")
        print('\n', '++++++++++++++++++++++++++++++++++++++++++++++++++++', '\n',
             '++++++++++++ SCRUBBING SIMULATION STARTED +++++++++++++++', '\n',
             '++++++++++++++++++++++++++++++++++++++++++++++++++++', '\n')
        QApplication.processEvents()
        current_set = float(self.currentEdit.text())
        # total_length needs to be caluclated for positioning the object in the scene
        total_length = 0
        eDosemin = float(self.minElectronDose.text())
        eDoseMax = float(self.maxElectronDose.text())
        steps = int(float(self.eDoseSteps.text()))
        eDoseRange = np.logspace(np.log10(eDosemin),np.log10(eDoseMax),num=steps)
        if Config.DataFile == "":
            QMessageBox.warning(self, "Specify a valid input file! ",
                                "Please select an Input file written in the 'New' format",
                                QMessageBox.Ok)
            self.scrubbingOp1PushButton.setText('Run Simulation')
            return
        listDensity = Scrubbing.runSimulation(current_set,eDoseRange)

        self.scrubbingOp1PushButton.setText('Run Simulation')
        self.ScrubbingPlot(eDoseRange, listDensity)


    def RunScrubbingSimulation(self):
        """
        Runs the simulation on the Scrubbing effect and plots the result in the tab 'Scrubbing Simulation'. See the user manual for more details.
        @return:  None
        """
        self.scrubbingOp2PushButton.setText("Running...")
        self.getESDFromDose()
        if Config.DataFile == "":
            QMessageBox.warning(self, "Specify a valid input file! ",
                                "Please select an Input file written in the 'New' format",
                                QMessageBox.Ok)
            self.scrubbingOp2PushButton.setText("Run Simulation")
            return
        Segments, EndPump, EndSource, DivisionList, GeometryParameters = GetSegments(Config.DataFile)

        total_length = 0
        try:
            GeometryParameters[0]
        except TypeError:
            QMessageBox.warning(self, "ERROR in Input Parameters",
                                "Please define the Input parameter correctly! Did you set the parameter name in the file? Do you have to change the input folder?",
                                QMessageBox.Ok)
            return
        for segment in GeometryParameters:
            # DivisionsList
            try:
                seg_length = float(segment[0]) / 1000.
                total_length += seg_length
            except:
                break

        # Segments2, EndPump2, EndSource2, DivisionList2, GeometryParameters2 = GetSegments(Config.DataFile2)   #second beam line
        if Segments == False:
            QMessageBox.warning(self, "ERROR in Input Parameters",
                                "Please define the Input parameter correctly! Could not find item: " + str(EndPump),
                                QMessageBox.Ok)
            self.scrubbingOp2PushButton.setText('Run Simulation')
            return
        print('number of segment', len(Segments))

        if not Segments:
            QMessageBox.warning(self, "ERROR: No File uploaded!", "Please upload a file with the input parameters!",
                                QMessageBox.Ok)

            self.scrubbingOp2PushButton.setText('Run Simulation')
            return

        # DENSITY PLOT
        current_set = float(self.currentEdit.text())
        den = Calculate(Segments, EndPump, EndSource, current_set)

        if den == []:
            QMessageBox.warning(self, "ERROR in Input Parameters",
                                "Ill-posed matrix equations lead to unsolveable system. Please define the Input parameters correctly!",
                                QMessageBox.Ok)
            self.scrubbingOp2PushButton.setText('Run Simulation')
            return
        try:
            den.H2
        except:
            QMessageBox.warning(self, "ERROR in Input Parameters",
                                "Please define the Input parameter correctly! Could not find item: " + str(den),
                                QMessageBox.Ok)
            self.scrubbingOp2PushButton.setText('Run Simulation')
            return

        self.ScrubbingPlot2(den)
        self.scrubbingOp2PushButton.setText('Run Simulation')

    def ScrubbingPlot2(self,den):
        """
        Plots the results from RunScrubbingSimulation2  in the Tab 'Dynamic pressure due to ESD'. See the User Guide for more information. 
        @param den: Density profile for the simulated system 
        @return: : None 
        """
        self.scrubbingPlotWidget.getPlotItem().clear()
        try:
            self.ScrubbingLegend.scene().removeItem(self.ScrubbingLegend)
        except:
            pass

        Plot = self.scrubbingPlotWidget.getPlotItem()
        self.ScrubbingLegend = Plot.addLegend()
        pen = pg.mkPen(color=str(Config.ColorPalette["ColorH2"].name()), width=5)
        p = Plot.plot(den.X, den.H2, pen=pen)
        self.ScrubbingLegend.addItem(p, "H<sub>2</sub>" )
        self.ScrubbingLegend.setFixedWidth(100)

        pen = pg.mkPen(color=str(Config.ColorPalette["ColorCH4"].name()), width=5)
        p = Plot.plot(den.X, den.CH4, pen=pen)
        self.ScrubbingLegend.addItem(p, "CH<sub>4</sub>")

        pen = pg.mkPen(color=str(Config.ColorPalette["ColorCO"].name()), width=5)
        p = Plot.plot(den.X, den.CO, pen=pen)
        self.ScrubbingLegend.addItem(p, "CO")

        pen = pg.mkPen(color=str(Config.ColorPalette["ColorCO2"].name()), width=5)
        p = Plot.plot(den.X, den.CO2, pen=pen)
        self.ScrubbingLegend.addItem(p, "CO<sub>2</sub>")




    def ScrubbingPlot(self,eDoseRange, listDensity):
        """
        Plots the result of the Scrubbing Simulation. \n
        Parameters:
        ----------
        @param eDoseRange: (list) Simulated values of received electron dose.
        @param listDensity: (list) Density profile for the different simulated electron doses.
        :return None:
        """
        print('Scrubbing Plot')
        X = listDensity[0].X
        n = len(listDensity)
        self.scrubbingPlotWidget.getPlotItem().clear()
        try:
            self.ScrubbingLegend.scene().removeItem(self.ScrubbingLegend)
        except:
            pass

        Plot = self.scrubbingPlotWidget.getPlotItem()
        self.ScrubbingLegend = Plot.addLegend()

        i = 0
        for edose, den in zip(eDoseRange, listDensity):
            pen = pg.mkPen(color=str(Config.ColorTuple[i].name()), width=5)
            p = Plot.plot(den.X, den.total(), pen=pen)
            self.ScrubbingLegend.addItem(p, "Accumulated electron dose of %.2E e<sup>-</sup>/cm<sup>2</sup>" % (edose))

            i += 1

        """
        try:
            print(self.names)
            for t in self.names:
                self.scrubbingLegend.removeItem(t)
            self.names = []
            self.plotScrubbing1.setData(x=[], y=[])
            self.plotScrubbing2.setData(x=[], y=[])
            self.plotScrubbing3.setData(x=[], y=[])
            self.plotScrubbing4.setData(x=[], y=[])
            self.plotScrubbing5.setData(x=[], y=[])
        except:
            self.names = []

        print(n)
        # print("ListCurrents = ", listCurrent[0],listCurrent[int(n / 3)],listCurrent[int(2*n / 3)],listCurrent[n])

        self.plotScrubbing1.setData(x=X, y=listDensity[0].total())
        self.scrubbingLegend.addItem(self.plotScrubbing1, name=" " + str(eDoseRange[0]) + " e/cm^2")
        self.names.append(" " + str(eDoseRange[0]) + " e/cm^2")

        self.plotScrubbing2.setData(x=X, y=listDensity[int(n / 4)].total())
        self.scrubbingLegend.addItem(self.plotScrubbing2, name=" " + str(eDoseRange[int(n / 4)]) + " e/cm^2")
        self.names.append(" " + str(eDoseRange[int(n / 4)]) + " e/cm^2")

        self.plotScrubbing3.setData(x=X, y=listDensity[int(2 * n / 4)].total())
        self.scrubbingLegend.addItem(self.plotScrubbing3, name=" " + str(eDoseRange[int(2 * n / 4)]) + " e/cm^2")
        self.names.append(" " + str(eDoseRange[int(2 * n / 4)]) + " e/cm^2")

        self.plotScrubbing4.setData(x=X, y=listDensity[int(3*n/4)].total())
        self.scrubbingLegend.addItem(self.plotScrubbing4, name=" " + str(eDoseRange[int(3*n/4)]) + " e/cm^2")
        self.names.append(" " + str(eDoseRange[int(3*n/4)]) + " e/cm^2")

        self.plotScrubbing5.setData(x=X, y=listDensity[n].total())
        self.scrubbingLegend.addItem(self.plotScrubbing5, name=" " + str(eDoseRange[n]) + " e/cm^2")
        self.names.append(" " + str(eDoseRange[n]) + " e/cm^2")
        """


    def create_actions(self):
        """
        Creates the different actions in the Menu.
        @return:  None
        """
        print('createActions')
        #File
        fileLoadAction = self.createAction("&Load...", self.fileLoad, "Ctrl+L")
        filePropertiesAction = self.createAction("&Properties",self.fileProperties, "Ctrl+P" )
        fileQuitAction = self.createAction("&Quit", self.close,"Ctrl+Q")

        fileMenu = self.menuBar().addMenu("File")
        fileMenuActions = (fileLoadAction,  filePropertiesAction, None, fileQuitAction)
        self.addActions(fileMenu, fileMenuActions)



        #Add&Edi
        addInputAction = self.createAction("&Simulation", self.fileMysimulations, "Ctrl+I" )
        addMaterialAction = self.createAction("&Material", self.materialNew, "Ctrl+M" )
        addPumpAction = self.createAction("&Pump",self.pumpNew, "Alt+P" )
        addGassourceAction = self.createAction("&Gassource", self.gassourceNew,"Ctrl+G")
        addCryoAction = self.createAction("&Cryogenics",self.CryogenicSetup, "Alt+C")
        addESDCurve = self.createAction("&ESD curve", self.ESDcurveNew,"Ctrl+D")



        addInputMenu = self.menuBar().addMenu("Add and Edit")
        addInputMenuActions = (addInputAction,addMaterialAction, addPumpAction, addGassourceAction,addCryoAction,addESDCurve)
        self.addActions(addInputMenu, addInputMenuActions)


        # Analysis
        analysisMenu = self.menuBar().addMenu("Analysis")
        analysisConfig = (self.createAction("&Analysis menu", self.AnalysisTab, "Alt+A"),)
        self.addActions(analysisMenu, analysisConfig)


        #Help
        helpMenu = self.menuBar().addMenu("Help")
        helpUsersGuide = self.createAction("&User's guide",self.openUserGuide,"Ctrl+H")
        helpDocumentation = self.createAction("&Documentation",self.openDocumentation, "Ctrl+U")
        helpMenuActions = (helpUsersGuide,helpDocumentation)
        self.addActions(helpMenu,helpMenuActions)




    #Functions needed for creating connections to button

    def PressureDensity(self):
        """
        Changes the results presented in the the tab 'Simulation' from density to pressure and  back
        @return:  None
        """
        print('PressureDensity')
        Density.setSensitivityFactor([float(self.h2SpinBox.value()), float(self.ch4SpinBox.value()), float(self.coSpinBox.value()), float(self.co2SpinBox.value())])
        den=Density.transformation()
        labelStyle = {'color': '#FFF', 'font-size': '14pt'}
        if Density.density == True:
            self.densityPlotWidget.setLabel('left', "Density", units='molecules/m<sup>3</sup>', **labelStyle)
        else:
            self.densityPlotWidget.setLabel('left', "Pressure", units='mbar', **labelStyle)
        self.updatePlot(den)

    def ShiftXAxis(self):
        """
        Shifts the X axis in the 'Simulation' tab
        @return: 
        """
        print('ShiftXAxis')
        shift= self.shiftEdit.text()
        if shift=="":
            shift="0"
        try:
            shift=float(shift)
            for i in range(len(Density.X)):
                Density.X[i]+= shift
        except:
            QMessageBox.warning(self, "Unsuccessful shift of x-axis", "Unsuccessful shift of x-axis: Please check your value!", QMessageBox.Ok)




    def oldfileDirectory(self):
        """
        """
        print('oldFileDirectory')
        self.uploadEdit.setText('')
        dir = (os.path.dirname(Config.DataFolder+'Input_old/'))# if self.filename is not None else Config.DataFolder+'Input/')
        fname = unicode(QFileDialog.getOpenFileName(self,"Choose CSV-file in old input format", dir))
        parts=fname.split('/')
        self.transformEdit.setText(parts[-1])
        self.nameEdit.setText(parts[-1][:-4])
        Config.OldDataFile=fname


    def fileLoad(self):
        """
        Loads Materials, Pumps and Gas sources
        @return:  None
        """
        print('fileLoad: Reload Materials, Pumps, Gassources')
        Config.Load()

        QMessageBox.information(self, "Load...", "Material, Pumps and Gassources have beeen reloaded! " , QMessageBox.Ok)

    def fileExternal(self):

        self.ex = ExternalDataWindow.ExDataWindow()
        self.ex.show()

    def fileShow(self):
        self.showWindow = ShowWindow.ShowWindow()
        self.showWindow.show()

    def fileMysimulations(self):

        self.mySimulations = MySimulationsWindow.MySimulationsWindow()
        self.mySimulations.show()

    def fileProperties(self):
        """
        Launches the Property Window
        @return:  None
        """
        self.ex = PropertyWindow.PropWindow()
        self.ex.show()

    def upload1Directory(self):
        """

        """
        print('uploadDirectory1')
        dir = (os.path.dirname(Config.DataFolder+'Output/'))
        fname = unicode(QFileDialog.getOpenFileName(self,"Choose CSV-file", dir))
        parts=fname.split('/')
        self.upload1DirectoryLabel.setText(parts[-1])
        Config.Upload1=fname

    def upload2Directory(self):
        """

        """
        print('uploadDirectory2')
        dir = (os.path.dirname(Config.DataFolder+'Output/'))
        fname = unicode(QFileDialog.getOpenFileName(self,"Choose CSV-file", dir))
        parts=fname.split('/')
        self.upload2DirectoryLabel.setText(parts[-1])
        Config.Upload2=fname


    def fileNew(self):
        """
        Sets the simulation Data file.
        """
        print('fileNew')
        dir = (os.path.dirname(Config.DataFolder+'Input/'))# if self.filename is not None else Config.DataFolder+'Input/')
        fname = unicode(QFileDialog.getOpenFileName(self,"PyVASCO - Choose CSV-file", dir))
        parts=fname.split('/')
        self.uploadEdit.setText(parts[-1])

        self.nameEdit.setText(parts[-1][:-4])
        Config.DataFile=fname

    def fileScrubbingNew(self):
        """
        Sets the simulation Data file.
        """
        print('fileScrubbingNew')
        dir = (
        os.path.dirname(Config.DataFolder + 'Input/'))  # if self.filename is not None else Config.DataFolder+'Input/')
        fname = unicode(QFileDialog.getOpenFileName(self, "PyVASCO - Choose CSV-file", dir))
        parts = fname.split('/')
        self.uploadEdit6.setText(parts[-1])

        Config.DataFile = fname

    def gaugesUpload(self):
        """
        Loads Gauges data file.
        """
        dir = (os.path.dirname(Config.GaugesFolder))
        fname = unicode(QFileDialog.getOpenFileName(self,"IdaVac - Choose CSV-file", dir))
        parts=fname.split('/')
        self.gaugesEdit.setText(parts[-1])
        Config.GaugesFile=fname


    def logScale(self):
        """
        Sets logarithmic scale in the results plot of tab 'Simulation'.
        """
        if self.logCheckBox.isChecked():
            log = True
        else: log = False
        self.densityPlotWidget.setLogMode(False, log)



    def PlottingQuality(self):
        """
        Sets number of points to be plotted in the pressure profile plot located in the tab 'Simulation'.
        """
        Config.NumPointsVacProfile = 30 * (self.plottingSlider.value() + 10)

    def inputNew(self):
        """
        Launches the 'New Input' window.
        """
        self.NewInputFile = NewInput.NewInputWindow()
        self.NewInputFile.show()

    def materialNew(self):
        """
        Launches the 'New Material' window.
        """
        self.MatNew = NewMaterialWindow.NewMatWindow()
        self.MatNew.show()

    def pumpNew(self):
        """
       Launches the 'New Pump' window.
       """
        self.PumpNew = NewPumpWindow.NewPumpWindow()
        self.PumpNew.show()

    def gassourceNew(self):
        """
        Launches the 'New Gas source' window.
        """
        self.GasSNew = NewGasSourceWindow.NewGSourceWindow()
        self.GasSNew.show()

    def CryogenicSetup(self):
        """
        Launches the 'Cryogenics setup' window
        """
        self.CryoWindow = CryoWindow.CryoWindow()
        self.CryoWindow.show()

    def ESDcurveNew(self):
        """
        Launches the 'New ESD curve' window.
        """
        self.ESDcurveNew = NewESDcurve.NewESDWindow()
        self.ESDcurveNew.show()

    def SEYcurveNew(self):
        """
        Launches the 'New SEY curve' window.
        """
        pass

    def AnalysisTab(self):
        self.AnalysisW = AnalysisWindow.AnalysisWindow()
        self.AnalysisW.show()

    def openUserGuide(self):
        """
        Opens the User guide.
        """
        userGuideFile = Config.DocsFolder + "UserGuide.pdf"
        webbrowser.open_new(userGuideFile)

    def openDocumentation(self):
        """
        Opens the API documantation.
        """
        docFile = Config.DocsFolder + "Documentation.html"
        webbrowser.open(docFile, new=2)

    def saveDirectory(self):
        """
        Sets the name of the Output file of the simulation.
        """
        dir = self.saveEdit.text()

        fname = unicode(QFileDialog.getExistingDirectory(self,"Saving in...", dir))
        self.saveEdit.setText(fname)

    def updatePlot(self, density):
        """
        Updates the plot in the 'Simulation' tab.
        @param density: (DensityClass): Result of the simulation.
        """
        self.ShiftXAxis()
        if self.h2CheckBox.isChecked():
            self.plotH2.setData(x = density.X,y = density.H2)

        else: self.plotH2.setData(x = [], y = [])
        if self.ch4CheckBox.isChecked(): self.plotCH4.setData(x = density.X, y = density.CH4)
        else: self.plotCH4.setData(x = [], y = [])
        if self.coCheckBox.isChecked(): self.plotCO.setData(x = density.X, y = density.CO)
        else: self.plotCO.setData(x = [], y = [])
        if self.co2CheckBox.isChecked(): self.plotCO2.setData(x = density.X, y = density.CO2)
        else: self.plotCO2.setData(x = [], y = [])
        if self.totalCheckBox.isChecked() and density.density is False:

            self.plot_total.setData(x = density.X, y = density.SensitivityTotal())
            self.densityPlotWidget.plotItem.legend.addItem(self.plot_total,"Total pressure")


        else:
            self.plot_total.setData(x = [], y = [])
            try:
                self.densityPlotWidget.plotItem.legend.removeItem('Total pressure')
            except:
                pass

        self.l.update()

    def updateLHCData(self):
        """
        Adds the data from the Gauges file to 'Simulation' plot.
        """
        self.plot_Data.setData(x = [], y = [])
        self.plot_Data_blue.setData(x = [], y = [])
        vals = []
        vals_blue = []
        if Config.GaugesFile == "":
            vals = []
            vals_blue =[]
        else:
            vals = Config.LoadLHCData(Config.GaugesFile)
            vals_blue = Config.LoadLHCData(Config.DataFolder+'Input/GaugesData/Gauges_5211_blue.csv')
        start = float(self.gaugesSpinbox.text())

        xvals = [row[0] - start for row in vals] #subtracting 12820.2 to match the coordinate systems...
        yvals = [row[1] for row in vals]
        yvals_max = [row[3] for row in vals]
        yvals_min = [row[2]  for row in vals]

        xvals_blue = [row[0] - start for row in vals_blue] #subtracting 12820.2 to match the coordinate systems...
        yvals_blue = [row[1] for row in vals_blue]
        yvals_max_blue = [row[3] for row in vals_blue]
        yvals_min_blue = [row[2]  for row in vals_blue]
        if self.pressureRadioButton.isChecked():
            self.plot_Data = self.densityPlotWidget.plot(x= xvals , y= yvals, pen= None, symbol = 'o', symbolSize = 5, symbolPen = (255, 255, 255, 200), symbolBrush = (0,0,255,150))
            self.plot_Data_blue = self.densityPlotWidget.plot(x= xvals_blue , y= yvals_blue, pen= None, symbol = '+', symbolSize = 5, symbolPen = (255, 255, 255, 200), symbolBrush = (0,0,255,150))
            self.densityPlotWidget.plotItem.legend.addItem(self.plot_Data,"LHC data")
            self.densityPlotWidget.plotItem.legend.addItem(self.plot_Data_blue, "LHC data")
        else:
            self.plot_Data = self.densityPlotWidget.plot(x= [] , y= [])
            try:
                self.densityPlotWidget.plotItem.legend.removeItem("LHC data")
                self.densityPlotWidget.plotItem.legend.removeItem("LHC data")
            except:
                pass
        self.l.update()

    def critCurrentPlot(self, listDensity,listCurrent):
        """
        Plot in the 'Critical Current' tab.
        @param listDensity: (list) List containing the density profile for the different simulated currents.
        @param listCurrent: (list) List with simulated beam currents.
        @return: None
        """
        print('crit current Plot')
        print(listCurrent)
        X = listDensity[0].X
        n = len(listDensity) - 1
        try:
            print(self.names)
            for t in self.names:
                self.critLegend.removeItem(t)
            self.names = []
            self.plotCurrent1.setData(x=[], y=[])
            self.plotCurrent2.setData(x=[], y=[])
            self.plotCurrent3.setData(x=[], y=[])
            self.plotCurrent4.setData(x=[], y=[])
        except:
            self.names = []

        print(n)
        #print("ListCurrents = ", listCurrent[0],listCurrent[int(n / 3)],listCurrent[int(2*n / 3)],listCurrent[n])
        if n >= 3:

            self.plotCurrent1.setData(x = X, y = listDensity[0].total())
            self.critLegend.addItem(self.plotCurrent1,name=" " + str(listCurrent[0]) + " A")
            self.names.append(" " + str(listCurrent[0]) + " A")

            self.plotCurrent2.setData(x = X, y = listDensity[int(n / 3)].total())
            self.critLegend.addItem(self.plotCurrent2, name=" " + str(listCurrent[int(n / 3)]) + " A")
            self.names.append(" " + str(listCurrent[int(n / 3)]) + " A")

            self.plotCurrent3.setData(x = X, y = listDensity[int(2 * n / 3)].total())
            self.critLegend.addItem(self.plotCurrent3, name=" " + str(listCurrent[int(2*n / 3)]) + " A")
            self.names.append(" " + str(listCurrent[int(2*n / 3)]) + " A")

            self.plotCurrent4.setData(x = X, y = listDensity[n].total())
            self.critLegend.addItem(self.plotCurrent4, name=" " + str(listCurrent[n]) + " A")
            self.names.append(" " + str(listCurrent[n]) + " A")

        elif n == 2:
            self.plotCurrent1.setData(x=X, y=listDensity[0].total())
            self.critLegend.addItem(self.plotCurrent1, name=" " + str(listCurrent[0]) + " A")
            self.names.append(" " + str(listCurrent[0]) + " A")

            self.plotCurrent2.setData(x=X, y=listDensity[1].total())
            self.critLegend.addItem(self.plotCurrent2, name=" " + str(listCurrent[1]) + " A")
            self.names.append(" " + str(listCurrent[1]) + " A")

            self.plotCurrent3.setData(x=X, y=listDensity[2].total())
            self.critLegend.addItem(self.plotCurrent3, name=" " + str(listCurrent[2]) + " A")
            self.names.append(" " + str(listCurrent[2]) + " A")

        else:
            self.plotCurrent1.setData(x=X, y=listDensity[0].total())
            self.critLegend.addItem(self.plotCurrent1, name=" " + str(listCurrent[0]) + " A")
            self.names.append(" " + str(listCurrent[0]) + " A")

            self.plotCurrent2.setData(x=X, y=listDensity[-1].total())
            self.critLegend.addItem(self.plotCurrent2, name=" " + str(listCurrent[1]) + " A")
            self.names.append(" " + str(listCurrent[-1]) + " A")







    def runSimulation(self):
        """
        Runs main simulation and plots the results in the 'Simulation' tab.
        """

        if self.ThreeDCheckBox.isChecked():
            # 3d plotting 
            w = gl.GLViewWidget()
            w.show()
            w.setWindowTitle('3d sketch')
            w.setCameraPosition(distance=50)
            w.resize(800,600)
            w.setBackgroundColor('w')




        print('\n', '++++++++++++++++++++++++++++++++++++++++++++++++++++', '\n',
              '++++++++++++ NEW SIMULATION STARTED +++++++++++++++', '\n',
              '++++++++++++++++++++++++++++++++++++++++++++++++++++', '\n')

        self.geometryPlotWidget.clear()
        self.densityRadioButton.click()
        Config.setMass([float(self.massEdit1.text()), float(self.massEdit2.text()), float(self.massEdit3.text()), float(self.massEdit4.text())])
        Config.setCrossSection([float(self.crossSectionEdit1.text()), float(self.crossSectionEdit2.text()), float(self.crossSectionEdit3.text()), float(self.crossSectionEdit4.text())])
        Config.TotalOutgassingForMaterials = ["BCu,BCu2"]#self.TotalOutgassingMaterials.text().split(",")
        self.runsimulationButton.setText('Running...')
        self.logScale()
        QApplication.processEvents()

        if Config.DataFile == "":
            QMessageBox.warning(self, "Specify a valid input file! ",
                                "Please select an Input file written in the 'New' format",
                                QMessageBox.Ok)
            self.scrubbingOp2PushButton.setText("Run Simulation")
            return
        Segments, EndPump, EndSource, DivisionList, GeometryParameters = GetSegments(Config.DataFile)

        #total_length needs to be caluclated for positioning the object in the scene
        total_length = 0
        try:
            print(GeometryParameters[0])
        except TypeError:
            QMessageBox.warning(self, "ERROR in Input Parameters", "Please define the Input parameter correctly! Did you set the parameter name in the file? Do you have to change the input folder?", QMessageBox.Ok)
            return
        for segment in GeometryParameters:
            #DivisionsList
            try:
                seg_length = float(segment[0])/1000.
                total_length += seg_length
            except:
                break

        if Segments == False:
            QMessageBox.warning(self, "ERROR in Input Parameters", "Please define the Input parameter correctly! Could not find item: " + str(EndPump) , QMessageBox.Ok)
            self.runsimulationButton.setText('Run Simulation')
            return
        print('number of segment', len(Segments))

        if not Segments:
            QMessageBox.warning(self, "ERROR: No File uploaded!", "Please upload a file with the input parameters!", QMessageBox.Ok)
            self.uploadEdit.setFocus()
            self.runsimulationButton.setText('Run Simulation')
            return

        #DENSITY PLOT
        current_set = float(self.currentEdit.text())
        den = Calculate(Segments, EndPump, EndSource, current_set)


        if den == []:
            QMessageBox.warning(self, "ERROR in Input Parameters", "Ill-posed matrix equations lead to unsolveable system. Please define the Input parameters correctly!"  , QMessageBox.Ok)
            self.runsimulationButton.setText('Run Simulation')
            return
        try: den.H2
        except:
            QMessageBox.warning(self, "ERROR in Input Parameters", "Please define the Input parameter correctly! Could not find item: "+ str(den) , QMessageBox.Ok)
            self.runsimulationButton.setText('Run Simulation')
            return
        Density.setDensity(den)
        Density.setTemperatureProfile(den.Temperature)

        if self.UseRecursivePumpingSpeedCheckButton.isChecked():

            # Modify segments:
            Segments, EndPump = SetPumpingSpeedforAvgPressure(Density,Segments,EndPump)
            den = Calculate(Segments, EndPump, EndSource, current_set)
            if den == []:
                QMessageBox.warning(self, "ERROR in Input Parameters",
                                "Ill-posed matrix equations lead to unsolveable system. Please define the Input parameters correctly!",
                                QMessageBox.Ok)
                self.runsimulationButton.setText('Run Simulation')
                return

            Density.setDensity(den)
            Density.setTemperatureProfile(den.Temperature)

        self.updatePlot(Density)
        self.updateLHCData()


        #Geometry
        l0 =self.shiftEdit.text()
        if l0 == "":
            l0="0"
        l0=float(l0)
        help_vertical = 0
        LegendMaterialDict= {}
        b_old = 0

        for segment in GeometryParameters:
            #DivisionsList
            try: l=float(segment[0])/1000.
            except: break
            b=float(segment[1])/1000.
            material=segment[2]
            temperature = float(segment[3])

            if temperature < 100:
                rect_magnet = QGraphicsRectItem(QRectF(l0, -0.15, l, 0.3))
                rect_magnet.setPen(QPen(Config.ColorPalette['LightGray']))
                rect_magnet.setBrush(QBrush(Config.ColorPalette['LightGray']))
                self.geometryPlotWidget.addItem(rect_magnet)



            rect=QGraphicsRectItem(QRectF(l0, -b/2+ help_vertical, l, b))
            rect.setPen(QPen(Config.ColorPalette['LightGray']))


            rect.setBrush(QBrush(
                Config.MaterialColorDict[material]
                ))
            l0+=l

            self.geometryPlotWidget.addItem(rect)
            LegendMaterialDict[material] = Config.MaterialColorDict[material]

            ## 3D Plotting 
            if self.ThreeDCheckBox.isChecked():
                md_help = gl.MeshData.cylinder(rows=10, cols=20, radius=[50.*b_old, 50.*b], length=0.01)
                md = gl.MeshData.cylinder(rows=10, cols=20, radius=[50.*b, 50.*b], length=l-0.01)
                b_old = b
                m_help = gl.GLMeshItem(meshdata=md_help, smooth=True, color=Config.MaterialColorDict[material],shader='shaded', glOptions='translucent')
                m1 = gl.GLMeshItem(meshdata=md, smooth=True, color=Config.MaterialColorDict[material],shader='shaded', glOptions='translucent')

                m_help.translate(0,0,l0-l-total_length*0.5)
                m_help.rotate(90., 1., 0., 0.)
                m1.translate(0,0,l0-l+0.01-total_length*0.5)
                m1.rotate(90., 1., 0., 0.)
                w.addItem(m_help)
                w.addItem(m1)
                # Save plot
                d = w.renderToArray((1000, 1000))
                filename = str(self.nameEdit.text()) + ".png"
                pg.makeQImage(d).save(filename)


        ###############################
#        l0=self.shiftEdit.text()
#        if l0 == "":
#            l0="0"
#        l0=float(l0)

#        for segment in GeometryParameters2:
#            #DivisionsList
#            try: l=float(segment[0])/1000
#            except: break
#            b=float(segment[1])/1000
#            material=segment[2]
#            temperature = float(segment[3])
#            print(l0)
#            if not(367.064 <= l0 <= 655.39):
#                if l0 < 367.064:
#                    help_vertical = -0.07
#                else:
#                    help_vertical = 0.07
#                rect=QGraphicsRectItem(QRectF(l0, -b/2 + help_vertical, l, b))
#                rect.setPen(QPen(Config.ColorPalette['LightGray']))
#                #rect.opaqueArea(QPen(Config.ColorPalette['Red']))  #QPen(Config.ColorPalette['Red'])

#                rect.setBrush(QBrush(
#                    Config.MaterialColorDict[material]
#                    ))


#                self.geometryPlotWidget.addItem(rect)
#                LegendMaterialDict[material] = Config.MaterialColorDict[material]
#            l0+=l

#############################3

        for element in LegendMaterialDict:
            print("LegendMaterialDict[element]",LegendMaterialDict[element]," element", element)
            self.geometryPlotWidget.plot(pen=LegendMaterialDict[element], name=element)


        if self.savetxtCheckBox.isChecked():
            self.saveFile([Density.X,Density.H2, Density.CH4, Density.CO, Density.CO2])
        self.runsimulationButton.setText('Run Simulation')
        if self.currentCheckBox.isChecked(): self.critCurrent2() #self.critCurrent()

        if self.ThreeDCheckBox.isChecked():
            w.grabFrameBuffer().save('3DPlot.png')

    #def runSimulation3(self):

    #    self.geometryPlotWidget.clear()
    #    self.densityRadioButton.click()
    #    Config.setMass([float(self.massEdit1.text()), float(self.massEdit2.text()), float(self.massEdit3.text()), float(self.massEdit4.text())])
    #    Config.setCrossSection([float(self.crossSectionEdit1.text()), float(self.crossSectionEdit2.text()), float(self.crossSectionEdit3.text()), float(self.crossSectionEdit4.text())])
    #    self.runsimulationButton.setText('Running...')
    #    self.logScale()
    #    QApplication.processEvents()
    #    Segments, EndPump, EndSource, DivisionList, GeometryParameters = GetSegments(Config.DataFile)

    def transformInput(self):
        """
        Transforms a CSV file written  with VASCO's input format into the new format for PyVASCO. See user manual for more information.
        """
        print('transformation Input')
        dir=Config.OldDataFile
        isTransformed= Main_Material_Transformation(dir)
        if isTransformed:
            dir = Config.DataFile
            parts=dir.split('/')
            #self.oldFormatFilePath=dir
            self.uploadEdit.setText(parts[-1])
            Config.DataFile=dir
            help=Config.CrossSection
            self.crossSectionEdit1.setText(str(help[0]))
            self.crossSectionEdit2.setText(str(help[1]))
            self.crossSectionEdit3.setText(str(help[2]))
            self.crossSectionEdit4.setText(str(help[3]))
            Config.Load() #Load material/pump/gassource again
        else:
            QMessageBox.warning(self, "ERROR: OldInput to new format was unsuccessful!", 'Could not open file! It exists already. Please close it and it will be overwritten then! ', QMessageBox.Ok)

    def critCurrent(self):
        """
        Computes the critical current for a given geometry.
        """
        print('crit Current')
        self.runsimulationButton.setText('Running...')
        self.critCurrentLabel.setText("Critical Current: not determined!")
        QApplication.processEvents()
        Segments, EndPump, EndSource, DivisionList, GeometryParameters  = GetSegments(Config.DataFile)


        if Segments == False:
            QMessageBox.warning(self, "ERROR in Input Parameters", "Please define the Input parameter correctly! Could not find item: "+ str(EndPump) , QMessageBox.Ok)
            return

        if not Segments:
            QMessageBox.warning(self, "ERROR: No File uploaded!", "Please upload a file with the input parameters!", QMessageBox.Ok)
            self.uploadEdit.setFocus()
            self.runsimulationButton.setText('Run Simulation')
            return

        #DENSITY PLOT

                #DENSITY PLOT
        initialCurrent = float(self.initialcurrentSpinBox.value())
        if initialCurrent == 0:
            initialCurrent = 1.0e-6

        endCurrent = float(self.endcurrentSpinBox.value())
        steps = int(self.stepscurrentSpinBox.value()) # number of simulations between initial current and end current

        ################################# CALCULATION OF THE CRITICAL CURRENT ####################################
        # 1.- Use bisection method to detect if the density becomes negative inside the selected range of values.
        # 2.- Determine the greatest value of I which gives place to positive mean density in its maximum at I0 = 1e-6 A.
        # 3.- Reset precission and move from the previously determined point to greater currents until a divergence in n
        # of the order of 1e6 times the value of n in the previous step.
        # 4.- Also quit if negative value in n is found and give the last I which gave positive n as Ic.
        # 5.- If no negative values in the interval...

        helpCurrent = 1.0e-6 # No beam. It is not set to 0 to avoid numerical problems
        try:
            raise Warning("Density profile at I = 0 A not determined!! Using InitialCurrent")
            DensityProfile = Calculate(Segments, EndPump, EndSource, Current=helpCurrent)
            maxInitialDensity = max(DensityProfile.total())
            xIndex = np.argmax(DensityProfile.total())
        except:
            DensityProfile = Calculate(Segments, EndPump, EndSource, Current=initialCurrent)

        try:
            DensityProfile.H2
            maxInitialDensity = max(DensityProfile.total())
            xIndex = np.argmax(DensityProfile.total())
        except:
            QMessageBox.warning(self, "ERROR in Input Parameters",
                                "Please define the Input parameter correctly! Could not find item: " + str(
                                    DensityProfile), QMessageBox.Ok)
            self.runsimulationButton.setText('Run Simulation')
            return

        listCurrent = [helpCurrent]
        listDensity = [DensityProfile]
        CritCurrent = None
        tol = 0.01 # A
        precision = (endCurrent - initialCurrent)/steps # A
        tol = precision*0.01
        bisec = True

        i = 0
        tmpCurrent = 0
        negatives = 0
        while i < steps:
            i+=1
            print("Step", i, "initialCurrent=", initialCurrent, "endCurrent=", endCurrent)
            helpCurrent = abs(endCurrent + initialCurrent) * 0.5
            print("Help current", helpCurrent)
            DensityProfile = Calculate(Segments, EndPump, EndSource, Current=helpCurrent)
            try:
                print("aDensityProfile.CH4[xIndex] < 0", DensityProfile.CH4[xIndex] < 0, "DensityProfile.H2[xIndex] < 0",
                      DensityProfile.H2[xIndex] < 0, "DensityProfile.CO2[xIndex] < 0", DensityProfile.CO2[xIndex] < 0)
                if DensityProfile.CH4[xIndex] < 0 or DensityProfile.H2[xIndex] < 0 or DensityProfile.CO[xIndex] < 0 or \
                                DensityProfile.CO2[xIndex] < 0:
                    print("Negative density profile !!!!!! This means that we have gone over the critical density")
                    negatives += 1
                    endCurrent = helpCurrent
                else:
                    if negatives > 0:
                        initialCurrent = helpCurrent
                        precision = (endCurrent - 1 - initialCurrent) / steps
                    break
            except:
                pass
        else:
            print("Critical Current <= ", helpCurrent)

        for i in range(steps):
            print("Step", i, "initialCurrent=", initialCurrent, "endCurrent=", endCurrent)
            helpCurrent = initialCurrent + precision * i
            print(i, "HelpCurrent", helpCurrent)
            DensityProfile = Calculate(Segments, EndPump, EndSource, Current=helpCurrent)
            try:
                print(DensityProfile.total()[xIndex]/ listDensity[-1].total()[xIndex])
                if DensityProfile.total()[xIndex]/ listDensity[-1].total()[xIndex] > 1e3 : #* listDensity[-1].total()[ xIndex]: and DensityProfile.total()[xIndex] > 0:
                    CritCurrent = helpCurrent
                    print('Critical current determined at', CritCurrent)
                    self.critCurrentLabel.setText("Critical Current: " + str(CritCurrent) + " A")
                    break

                if DensityProfile.CH4[xIndex] < 0 or DensityProfile.H2[xIndex] < 0 or DensityProfile.CO[xIndex] < 0 or \
                                DensityProfile.CO2[xIndex] < 0:
                    maxCritDensity = DensityProfile.total()[xIndex]
                    CritCurrent = helpCurrent-precision

                    DensityProfile = Calculate(Segments, EndPump, EndSource, Current=helpCurrent - precision/2)
                    try:
                        if DensityProfile.CH4[xIndex] > 0 and DensityProfile.H2[xIndex] > 0 and DensityProfile.CO[xIndex] > 0 and \
                        DensityProfile.CO2[xIndex] > 0 and DensityProfile.total()[xIndex] > maxCritDensity:
                            CritCurrent = helpCurrent - precision/2
                            listCurrent.append(CritCurrent)
                            listDensity.append(DensityProfile)
                            print('Critical current determined at', CritCurrent)
                            self.critCurrentLabel.setText("Critical Current: " + str(CritCurrent) + " +- "+str(precision/2)+ " A")
                            break
                    except:
                        pass
                    print('Critical current determined at', CritCurrent)
                    self.critCurrentLabel.setText("Critical Current: " + str(CritCurrent) +" +- " + str(precision)+ " A")
                    break
                else:
                    if negatives > 0:
                        print('Critical current determined at', endCurrent)
                        self.critCurrentLabel.setText(
                            "Critical Current: " + str(endCurrent) + " +- " + str(precision) + " A")
                    else:
                        print("Critical Current >=", endCurrent)
                        self.critCurrentLabel.setText(
                            "Critical Current >= " + str(endCurrent) + " A")
                listCurrent.append(helpCurrent)
                listDensity.append(DensityProfile)
                #else:
                #    print("Critical Current >=", endCurrent)
            except:
                pass

        # Sort currents and corresponding density profiles in ascending order
        listCurrent,listDensity = zip(*sorted(zip(listCurrent,listDensity),key=lambda x: x[0]))
        listCurrent = list(listCurrent)
        listDensity = list(listDensity)
        print(listCurrent, type(listCurrent))
        # Plot the density for the different species where the density at I = 0 was maximum as a function of the current

        densityValue0 = []
        densityValue1 = []
        densityValue2 = []
        densityValue3 = []

        for element in listDensity:
            densityValue0.append(element.H2[xIndex])
            densityValue1.append(element.CH4[xIndex])
            densityValue2.append(element.CO[xIndex])
            densityValue3.append(element.CO2[xIndex])

        self.CurrentDyn1Plot.setData(x=listCurrent, y=densityValue0)
        self.CurrentDyn2Plot.setData(x=listCurrent, y=densityValue1)
        self.CurrentDyn3Plot.setData(x=listCurrent, y=densityValue2)
        self.CurrentDyn4Plot.setData(x=listCurrent, y=densityValue3)

        self.critCurrentPlot(listDensity, listCurrent)
        self.runsimulationButton.setText('Run Simulation')


        # Original Ida's algorithm
        '''
        current_stepsize = (endCurrent-int(initialCurrent))/steps
        print('current_stepsize', current_stepsize)

        helpCurrent=initialCurrent
        DensityProfile = Calculate(Segments, EndPump, EndSource, Current=helpCurrent)
        try: DensityProfile.H2
        except: 
            QMessageBox.warning(self, "ERROR in Input Parameters", "Please define the Input parameter correctly! Could not find item: "+ str(DensityProfile) , QMessageBox.Ok)
            self.runsimulationButton.setText('Run Simulation')
            return 
        listCurrent=[helpCurrent]
        listDensity=[DensityProfile]

        CritCurrent=0
        timesinif = 0
        for step in range(1,steps):
            #print("STEP : ", step)
            helpCurrent=initialCurrent+step*current_stepsize
            DensityProfile = Calculate(Segments, EndPump, EndSource, Current=helpCurrent)
            Residum=np.array(DensityProfile.total())-np.array(listDensity[-1].total())
            #print("RESIDUM",step,"=",Residum)
            #print("Min residum = ", min(Residum))
            if min(Residum) < 0:
                timesinif += 1
                CritCurrent = helpCurrent - current_stepsize
                self.critCurrentLabel.setText("Critical Current: " + str(CritCurrent) + " Ampere")
                #self.critCurrentLabel.setPalette(QPalette().setColor(QPalette.Foreground, QColor(255,80,80)))
                #break


            listCurrent.append(helpCurrent)
            listDensity.append(DensityProfile)

        print("listCurrent=",listCurrent)

        # Take the index of x , where the density assumes its maximum for hydrogen (h2 provides usually the highest density) 
        xIndex=np.argmax(listDensity[-1].H2) 
        xIndex+=2

        #max(xrange(len(listDensity[-1].H2)),key=listDensity[-1].H2.__getitem__)

        densityValue0=[]
        densityValue1=[]
        densityValue2=[]
        densityValue3=[]

        for element in listDensity:
            densityValue0.append(element.H2[xIndex])
            densityValue1.append(element.CH4[xIndex])
            densityValue2.append(element.CO[xIndex])
            densityValue3.append(element.CO2[xIndex])

        self.CurrentDyn1Plot.setData(x=listCurrent, y=densityValue0)
        self.CurrentDyn2Plot.setData(x=listCurrent, y=densityValue1)
        self.CurrentDyn3Plot.setData(x=listCurrent, y=densityValue2)
        self.CurrentDyn4Plot.setData(x=listCurrent, y=densityValue3)


        ##########Compare the density increase and DETERMINE THE CRITICAL CURRENT
        Density_0=listDensity[0].total()
        CritCurrent=0
        help=0
        for densityElement in listDensity:
            Density_1=densityElement.total()
            Residum=np.array(Density_1)-np.array(Density_0)
            if min(Residum) < 0:
                CritCurrent = listCurrent[help-1]
                break
            #print('Residum at current index ',current_value[help3], 'with value', max(abs(Residum)),'and', min(Residum))
            Density_0=Density_1
            help+=1    

        print('Critical current determined at',CritCurrent)
        self.critCurrentPlot(listDensity,listCurrent)
        self.runsimulationButton.setText('Run Simulation')
        '''

    def critCurrent2(self):
        """
        Implements computation of the Critical Current using the same algorithm used in VASCO. \n

        Description
        ===========

            1. Read values for Initial current (current from which the Ic is going to be computed), step (current
         increase between consecutive calculations), nsteps (maximum number of steps in the calculation) \n
            2. Set maximum relative increase between 2 consecutive computations of the average density. Why in VASCO is
         set to Ic_step = tan(88/90*pi/2) ? \n
            3. Conditions for finishing the computation: Relative increase in consecutive steps > Ic_step OR the
         minimum density for the gas with smaller density becomes negative OR  end of steps. \n
            4. Check if the density decreases with respect to the previous step. If so, stop the calculation and raise a
         warning.

        """
        # Implements computation of the Critical Current using the same algorithm used in VASCO

        ##################################    CALCULATION OF THE CRITICAL CURRENT ######################################
        # 1.- Read values for Initial current (current from which the Ic is going to be computed), step (current
        # increase between consecutive calculations), nsteps (maximum number of steps in the calculation)
        # 2.- Set maximum relative increase between 2 consecutive computations of the average density. Why in VASCO is
        # set to Ic_step = tan(88/90*pi/2) ?
        # 3.- Conditions for finishing the computation: Relative increase in consecutive steps > Ic_step OR the
        # minimum density for the gas with smaller density becomes negative OR  end of steps.
        # 4.- Check if the density decreases with respect to the previous step. If so, stop the calculation and raise a
        # warning.

        print('crit Current')
        notDetermined = False
        self.runsimulationButton.setText('Running...')
        self.critCurrentLabel.setText("Critical Current: not determined!")
        QApplication.processEvents()
        Segments, EndPump, EndSource, DivisionList, GeometryParameters = GetSegments(Config.DataFile)


        if Segments == False:
            QMessageBox.warning(self, "ERROR in Input Parameters",
                                "Please define the Input parameter correctly! Could not find item: " + str(EndPump),
                                QMessageBox.Ok)
            return

        if not Segments:
            QMessageBox.warning(self, "ERROR: No File uploaded!", "Please upload a file with the input parameters!",
                                QMessageBox.Ok)
            self.uploadEdit.setFocus()
            self.runsimulationButton.setText('Run Simulation')
            return

            # DENSITY PLOT
        initialCurrent = float(self.initialcurrentSpinBox.value())
        if initialCurrent == 0:
            initialCurrent = 1.0e-6

        precision = float(self.precisioncurrentSpinBox.value())
        steps = int(self.stepscurrentSpinBox.value())  # number of simulations between initial current and end current

        Ic_step = np.tan(88/90*np.pi*0.5)*1e3

        listDensity = [Calculate(Segments, EndPump, EndSource, Current=initialCurrent)]
        listCurrent = [initialCurrent]

        for step in range(1,steps+1):
            print("Step : ", step)
            # Compute the maximum of the average density for the initial current.
            helpCurrent = initialCurrent + precision * step
            print("HelpCurrent :", helpCurrent)
            print(step, "HelpCurrent", helpCurrent)
            DensityProfile = Calculate(Segments, EndPump, EndSource, Current=helpCurrent)

            print("max(np.array(DensityProfile.total()) - np.array(listDensity[-1].total()))/max(np.array(listDensity[-1].total())")
            print(max(np.array(DensityProfile.total()) - np.array(listDensity[-1].total())) / max(np.array(listDensity[-1].total())))

            if min([min(DensityProfile.H2),min(DensityProfile.CH4),min(DensityProfile.CO), min(DensityProfile.CO2)])< 0:
                print("Found negative density!")
                break

            elif max(np.array(DensityProfile.total()) - np.array(listDensity[-1].total()) ) < 0:
                print("Density decreases with increasing current!")
                break

            elif max(np.array(DensityProfile.total()) - np.array(listDensity[-1].total()))/max(np.array(listDensity[-1].total())) > Ic_step*precision :
                print("Critical current determined!")
                break

            listDensity.append(DensityProfile)
            listCurrent.append(helpCurrent)

        else:
            notDetermined = True
            print('Critical current not determined! ')
            self.critCurrentLabel.setText("Critical Current > " + str(helpCurrent) + " A")

        if step < 2:
            print('Warning: out of critical current loop at first step. Initial current value too high !!!!')
            QMessageBox.warning(self,'Warning: out of critical current loop at first step',' Initial current value too high !!!!' , QMessageBox.Ok)
            self.runsimulationButton.setText('Run Simulation')


        elif notDetermined is False:
            CritCurrent = helpCurrent - precision
            print('Critical current determined at', CritCurrent)
            self.critCurrentLabel.setText("Critical Current: " + str(CritCurrent) + " +- " + str(precision) + " A")

        # Plot the density for the different species where the density at I = 0 was maximum as a function of the
        #  current
        xIndex = np.argmax(listDensity[-1].H2)
        densityValue0 = []
        densityValue1 = []
        densityValue2 = []
        densityValue3 = []

        for element in listDensity:
            densityValue0.append(element.H2[xIndex])
            densityValue1.append(element.CH4[xIndex])
            densityValue2.append(element.CO[xIndex])
            densityValue3.append(element.CO2[xIndex])

        self.CurrentDyn1Plot.setData(x=listCurrent, y=densityValue0)
        self.CurrentDyn2Plot.setData(x=listCurrent, y=densityValue1)
        self.CurrentDyn3Plot.setData(x=listCurrent, y=densityValue2)
        self.CurrentDyn4Plot.setData(x=listCurrent, y=densityValue3)

        self.critCurrentPlot(listDensity, listCurrent)
        self.runsimulationButton.setText('Run Simulation')


    def saveFile(self,Array):
        """
        Saves the simulation results to CSV file in the directory indicated in the 'Data' tab under the label 'Save results in folder'

        @param Array: (numpy.ndarray) Array containing the density or pressure profile for the different considered species.
        """
        print('saveFile')
        #Array = [X, H2, CH4, CO, CO2] saves the values of array in a txt-file.
        fmtStrZone = "%d-%m-%Y_%H-%M-%S"
        utc = datetime.now(timezone('UTC'))
        if self.saveEdit.text()=='': self.saveEdit.setText(Config.VacProfileOutputFolder)
        dir = self.saveEdit.text()+ '\\' + self.nameEdit.text() +'_' + utc.strftime(fmtStrZone) + '.csv'
        #f=open(dir,'w+')
        try: f=open(dir,'w+')
        except IOError as e:
            QMessageBox.warning(self, "ERROR: Saving File -  Access denied!", "Read-Only Mode in this saving Directory! Please choose another directory or change the privacy properties! "  , QMessageBox.Ok)
            return
        f.write('X , H2, CH4, CO, CO2 \n')
        i=0
        while i<len(Array[0]):
            f.write(str(Array[0][i])+','+str(Array[1][i])+','+str(Array[2][i])+','+str(Array[3][i])+','+str(Array[4][i])+'\n')

            i+=1
        f.close()

    def take_screenshot(self):
        p = QPixmap.grabWindow(self.densityPlotWidget.winId())
        p.save(os.path.dirname(Config.DataFolder+'Output/')+'Screenshot.png', 'png',100)

    #interne Funktionen
    def initiateMainWindow(self):
        """
        Initializes the main window of PyVASCO.
        """

        list=[self.densityRadioButton, self.h2CheckBox, self.ch4CheckBox, self.coCheckBox, self.co2CheckBox, self.logCheckBox]
        for button in list:
            button.setChecked(True)

        self.nameEdit.setText("Unnamed")
        self.saveEdit.setText(os.path.dirname(Config.DataFolder+'Output/'))

    def checkallgas(self):
        """
        Selects the check-buttons of all gas species in the tab 'Data'

        """
        list=[self.h2CheckBox, self.ch4CheckBox, self.coCheckBox, self.co2CheckBox]
        if self.allgasCheckBox.isChecked():
            for button in list:
                button.setChecked(True)
                button.setDisabled(True)
        else:
            for button in list:
                button.setChecked(False)
                button.setDisabled(False)


    def okToContinue(self):
        pass
        '''
        if self.dirty:
            reply = QMessageBox.question(self,
                    "Image Changer - Unsaved Changes",
                    "Save unsaved changes?",
                    QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                return False
            elif reply == QMessageBox.Yes:
                return self.fileSave()
        return True
        '''



    def createAction(self, text, slot=None, shortcut=None, icon=None,tip=None, checkable=False):
        """
        Creates an action in the Menu and vinculates a keyboard shortcut. \n

        @param text: (str) Name of the action.
        @param slot: (optional, str)
        @param shortcut: (str) Definition of the action's shortcut.
        @param icon: (optional, str) Name of the PNG icon for the action.
        @param tip: (optional, str) Short description of the action.
        @param checkable: (optional, bool) If True, makes the action checkable.

        """
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/{0}.png".format(icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action

    def addActions(self, target, actions):
        """
        Adds actions to the targeted object. \n

        @param target: (PyQTWindow.Menu) Object where to add the specified list of Actions
        @param actions: (list) Actions to be added.
        """
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def center(self):
        """
        Places the Main Window of PyVASCO in the top left corner of the sceen.
        """
        frameGm = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        self.move(frameGm.topLeft())