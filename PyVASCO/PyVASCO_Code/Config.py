import os
import sys
from PyQt4.QtGui import QColor
import numpy as np
import pickle
import math
import numericalunits as nu
nu.reset_units()

from Computation import dataDensity
from Components import Material, Pump, Gassource
from os import listdir
from os.path import isfile, join
import platform



class ConfigClass():
    # e.g. set default values:
    # OutgassingFile = os.path.dirname(os.path.realpath(__file__)) +  \
    # '/' + 'Data/' + 'Output/IUVSTA_MBA_DL_QdZ_Ida3.csv'
    # DataFile = os.path.dirname(os.path.realpath(__file__)) +  \
    # '/' + 'Data/' + 'Input/IUVSTA_Taiwan2.csv'

    #DataFile = "."
    OldDataFile = "."
    CrossSection = np.array([4.45E-23, 3.18E-22, 2.75E-22, 4.29E-22])
    Upload1 = "."  # Tab4
    Upload2 = "."  # Tab4

    OutgassingFile = "."
    PhotonFile = "."
    ElectronFile = "."

    # Half-Gap [mm] for the TDI simulation
    halfGap = 50

    # ----------------PROJECT VARIABLES---------------------
    ProjectFolder = os.path.dirname(os.path.realpath(__file__)) + '/' ##os.path.dirname(sys.argv[0]) + "/"
    DataFolder = ProjectFolder + 'Data/'
    DataFile =  "" #'Input/Materials/CMS/CMS_7_Mar_red_with_external_example.csv'   # second beamline
    DataFile2 =  DataFolder + 'Input/Materials/CMS/CMS_8_mars_blue_example.csv'   # second beamline
    GaugesFile = ""


    #IconFolder = DataFolder + 'images/'

    ColorPalette = {
        'Red': QColor(255, 80, 80),
        'LightRed': QColor(255, 140, 140),
        'Blue': QColor(60, 120, 255),
        'LightBlue': QColor(120, 180, 255),
        'Gray': QColor(150, 150, 150),
        'LightGray': QColor(180, 180, 180),
        'RedA': QColor(255, 80, 80, 180),
        'BlueA': QColor(60, 120, 255, 180),
        #'ColorH2': QColor(255, 0, 0),
        #'ColorCH4': QColor(255, 128, 0),
        #'ColorCO': QColor(0, 0, 255),
        #'ColorCO2': QColor(128, 0, 0),
        'ColorH2': QColor(237, 129, 94),
        'ColorCH4': QColor(199, 176, 105),
        'ColorCO': QColor(126, 166, 149),
        'ColorCO2': QColor(138, 124, 145),
        'Colortotal': QColor(255, 46, 112),
        }
    ColorTuple = [j for i,j in ColorPalette.items()]

        #    'ColorH2': QColor(255, 80, 80),
        #'ColorCH4': QColor(255, 200, 140),
        #'ColorCO': QColor(60, 120, 255),
        #'ColorCO2': QColor(120, 255, 60)

         #       'ColorH2': QColor(255, 80, 80),
        #'ColorCH4': QColor(128, 0, 0),
        #'ColorCO': QColor(0, 153, 153),
        #'ColorCO2': QColor(0, 0, 153),
        #'Colortotal': QColor(255, 0, 0),

    # --------------- Documentation---------------------
    DocsFolder = ProjectFolder + "docs/"
    # -----------------PyVASCO---------------------------
    # replaced by nu.mol: Avogadro = 6.02214199e23  # mol-1
    kB =  1.3806488e-23      # JK-1 nu.kB
    e = 1.602176565e-19    # C
    Avogadro =  6.022140857e23
    RoomTemperature = 300
    Radius = 2963.340263  # m
    TotalLength = 26658.8832  # m
    NGas = 4  # [H2, CO, CH4, CO2]
    Mass = np.array(
        [2.01588, 16.0425, 28.0101, 44.0095]) / 1000 / 6.02214199e23  # [kg]

    Current = 0.5  # [Amperes]

    MaximumDivisions = 128 * 4
    MaxValueLimit = 1e3
    NumPointsVacProfile = 500  # determines the plotting quality

    ZoomPlot = 200
    ScalingXAxis = 0.10

    MaterialFolder = DataFolder + 'Input/Materials/'
    CryogenicsFolder = DataFolder +'Input/Cryogenics/'
    PumpFolder = DataFolder + 'Input/Pumps/'
    GassourceFolder = DataFolder + 'Input/Gassource/'

    GaugesFolder = DataFolder + 'Input/GaugesData/'
    VacProfileOutputFolder = DataFolder + 'Output/'
    #logFile = ProjectFolder + "log.txt"

    # Esd file example unbacked copper
    EsdFile = DataFolder + "ESD_and_SEY_unbaked_copper.csv"

    # TDIS Simulation Default parameters
    ESDFolder = DataFolder + "Input/ESD/"
    SEYFolder = DataFolder + "Input/SEY/"
    TDISFile = DataFolder + "Input/TDIS_dynamic_New.csv"
    SEYHomogeneousFile = SEYFolder + "TDIS_current.csv"

    Materials = {}
    Pumps = {}
    Gassources = {}
    MaterialColorDict = {}

    def __init__(self):
        print('ConfigClass Constructor')
        self.Load()
        self.useESDCurve = False
        self.eDose = 0
        self.uploadElectronFluxFromSEY = False
        self.currentSey = 1.0
        self.TotalOutgassingForMaterials = []


    def Load(self):
        print('Load: Materials, Pumps, Gassource')
        self.Materials = self.LoadMaterials()
        self.MaterialColorDict = self.MaterialColor()
        self.Pumps = self.LoadPumps()
        self.Gassources = self.LoadGassource()
        self.EquilibriumVaporPressure = self.LoadEquilibriumVaporPressure()

    def setMass(self, array):
        print ' changeof molecular mass'
        self.Mass = np.array(array) * 1 / 1000 / self.Avogadro

    def setCrossSection(self, array):
        print 'change of crosssection'
        self.CrossSection = np.array(array)

    def MaterialColor(self):
        MaterialColorDict = dict(zip(
            ['NEG', 'BeamScreen', 'BeamScreen_Cold', 'Cu', 'Be'],
            [QColor(250, 0, 0), QColor(0, 0, 133),
             QColor(0,0,255), QColor(153, 76, 0), QColor(255, 69, 0)]
            ))
        colors = [
            #QColor(66,0,133),
            QColor(133,0,133),
            QColor(133, 0, 66), QColor(0, 66, 133), QColor(0, 0, 194),
            QColor(0, 0, 255), QColor(133, 0, 0), QColor(0, 133, 133),
            QColor(255, 255, 0), QColor(194, 194, 0), QColor(133, 66, 0),
            QColor(0, 133, 66), QColor(0, 133, 0), QColor(66, 133, 0),
            QColor(133, 133, 0),
            QColor(244,244,66),QColor(164,66,244),
            QColor(30, 30, 30), QColor(181, 137, 0), QColor(203, 75, 22),
            QColor(220, 50, 47), QColor(211, 54, 130), QColor(108, 113, 196),
            QColor(38, 139, 210), QColor(42, 161, 152), QColor(181, 137, 0),
            QColor(203, 75, 22), QColor(220, 50, 47), QColor(211, 54, 130),
            QColor(108, 113, 196), QColor(38, 139, 210), QColor(42, 161, 152)
            ]
        help = 0
        for M in self.Materials:
            if M not in MaterialColorDict:
                if help == len(colors):
                    print ' material colors is repeating itself '
                    help = 0
                MaterialColorDict[M] = colors[help]
                help += 1

        return MaterialColorDict

    def LoadMaterials(self):
        print('LoadMaterial')

        FileList = [
            f for f in listdir(self.MaterialFolder)
            if isfile(join(self.MaterialFolder, f))
            ]
        Materials = {}
        for File in FileList:
            M = Material.Material(self.MaterialFolder + File)
            try:
               Materials[M.Name] = M
            except:
               pass
        return Materials

    def LoadPumps(self):
        print('LoadPump')
        # loop through the Pumpfolder and creates a dictionary "Pumps"
        #FileList = [
        #    f for f in listdir(self.PumpFolder)
        #    if (isfile(join(self.PumpFolder, f)) or os.path.isdir(f))
        #    ]
        FileList = listdir(self.PumpFolder)
        Pumps = {}
        for File in FileList:
            P = Pump.Pump(self.PumpFolder + File)
            Pumps[P.Name] = P
        # Check if zero pump already exists:
        if 'P0' in Pumps.keys():
            if any(Pumps['P0'].Speed != [0, 0, 0, 0]):
                print("P0 is reserved for zero-gasrelease!")
                # EXIT
        else:
            caption_Pump = [
                'S_H2 [l/s]', 'S_CH4 [l/s]', 'S_CO [l/s]', 'S_CO2 [l/s]'
                ]
            dir_Pumps = self.PumpFolder + 'P0' + '.csv'
            f = open(dir_Pumps, 'w+')
            f.write('P0' + ',' + '\n')
            for i in range(4):
                f.write(caption_Pump[i] + ',' + str(0) + '\n')
            f.close()
            P = Pump.Pump(dir_Pumps)
            Pumps[P.Name] = P
        return Pumps

    def LoadGassource(self):
        print('LoadGassource')
        FileList = [
            f for f in listdir(self.GassourceFolder)
            if isfile(join(self.GassourceFolder, f))
            ]
        Gassources = {}
        for File in FileList:
            G = Gassource.Gassource(self.GassourceFolder + File)
            Gassources[G.Name] = G

        # Check if zero gas-release already exists
        if 'G0' in Gassources.keys():
            if any(Gassources['G0'].GasRelease != [0, 0, 0, 0]):
                print("G0 is reserved for zero-gasrelease!")
                # EXIT
        else:
            caption_Gassource = [
                'g_H2 [l/s]', 'g_CH4 [l/s]', 'g_CO [l/s]', 'g_CO2 [l/s]'
                ]
            dir_Gassources = self.GassourceFolder + 'G0' + '.csv'
            f = open(dir_Gassources, 'w+')
            f.write('G0' + ',' + '\n')
            for i in range(4):
                f.write(caption_Gassource[i] + ',' + str(0) + '\n')
            f.close()
            G = Gassource.Gassource(dir_Gassources)
            Gassources[G.Name] = G

        return Gassources

    def AddMaterial(self, File):
        print "In AddMaterial"
        M = Material.Material(self.MaterialFolder + File)
        self.Materials[M.Name] = M
        print M.Name
        self.MaterialColorDict = self.MaterialColor()

    def LoadLHCData(self, file= GaugesFolder + 'Gauges_5211_red.csv', delimiter=','):
        print file
        try:
            with open(file,'r') as f:
                Array=[]
                f.next()
                for line in f: # f.readlines():
                    line = line.split(delimiter)
                    Array.append([float(line[0]), float(line[1]), float(line[2]), float(line[3])] )   
                f.close()
                return Array
        except Exception as ex:
            print('***Failed to read in gauges file! *** \n \n' + str(ex))
            return []

    def LoadTDISNonHomogeneous(self):
        self.CasesEFluxSEY = {
            "Case 1": [1.6, [1.6, 1.0], [Config.SEYFolder + f for f in os.listdir(Config.SEYFolder) if "EFlux" in f and "baseline.csv" in f],
                       "SEY 1.6 everywhere except the Jaws in Tanks 1,2 with SEY 1.0"],
            "Case 2": [1.6, [1.6, 1.0], [Config.SEYFolder +f for f in os.listdir(Config.SEYFolder) if "EFlux" in f and "coatedJ3.csv" in f],
                       "SEY 1.6 everywhere except the jaws in all three tanks with SEY 1.0"],
            "Case 3": [1.0, [1.6, 1.0], [Config.SEYFolder +f for f in os.listdir(Config.SEYFolder) if "EFlux" in f and "coatedBS.csv" in f],
                       "SEY 1.6 everywhere except the jaws in Tanks 1,2 and beam screen in all three tanks with SEY 1.0"],
            "Case 4": [1.0, [1.6, 1.0],
                       [Config.SEYFolder + f for f in os.listdir(Config.SEYFolder) if "EFlux" in f and "coatedJ3BBS.csv" in f],
                       "The jaws and beam screen and all three tanks with SEY 1.0, the rest is SEY 1.6"]}

    def AddTDISCaseStudy(self,BSSEY,maxminSEY,Files,Description):
        self.CasesEFluxSEY["Case " + str(len(self.CasesEFluxSEY.keys())+1)] = [BSSEY,maxminSEY,Files,Description]

    def DeleteTDISCaseStudy(self,Description):
        for k in self.CasesEFluxSEY.keys():
            if self.CasesEFluxSEY[k] == Description:
                del self.CasesEFluxSEY[k]

    def LoadEquilibriumVaporPressure(self):
        kB = 1.3806488e-23
        VaporPressure = pickle.load(open(self.DataFolder + "Input/VapPressure/VaporPressure.p"))
        nEq = []
        for k in ["H2","CH4","CO","CO2"]:
            nEq.append(np.array([np.array(VaporPressure[k])[:,0],np.array(VaporPressure[k])[:,1]*1.33e2/ kB/self.RoomTemperature]))
        self.nEq = nEq
        self.maxNeq = np.array([1e-4,1e-10,1e-10,1e-10])*1.33e2/kB
Config = ConfigClass()
