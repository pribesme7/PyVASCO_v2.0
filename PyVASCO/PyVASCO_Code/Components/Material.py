import numpy as np
import unit
from ESD import ESD
from TDI import TDIS
import os


class Material:
    """
    Parameters
    ==========
    
    B{File} (str): Name of the directory containing the Material \n

    Attributes
    ==========
    
    B{File} (str) : Name of the directory containing the Material \n
    B{Name}(str) : Name of the Material, typically M + Number \n
    B{Sticking} (numpy.array) : Sticking coefficient for the different gas species \n
    B{EtaI} (numpy.ndarray) : Ion induced gas desorption coefficients for the different gas species \n
    B{EtaE} (numpy.ndarray) : Electron induced gas desorption coefficients for the different gas species \n
    B{EtaPh} (numpy.ndarray) : Photon induced gas desorption coefficients for the different gas species \n
    B{OutGassing} (numpy.array) : Thermal outgassing per unit length for the different gas species \n
    B{LinearPumping} (numpy.array) : Wall pumping speed (for example getter coating) per unit length for the different
    gas species\n
    B{esdLoaded} (bool): True if the ESD vs. electron dose for the material has to be loaded; False otherwise \n
    B{seyLoaded} (bool): True if the ESD vs. electron dose for the material has to be loaded; False otherwise \n


    Methods
    =======
        - LoadESDCurve()
        - LoadSEYCurve()
        - showAll_Material()

    """
    Name = ''
    Sticking = []
    OutGassing = []   # molecule/m2/s
    LinearPumping = []  # m2/s
    EtaI = []  # molecules/ion
    EtaE = []  # molecules/electron
    EtaPh = []  # molecules/photon

    def __init__(self, File):
        print('Material Constructor')
        isSingleGas = False
        self.File = File
        LArray = []
        with open(File) as f:
            i = 0
            for line in f.readlines():
                lsplit = line.strip("\n").split(',')
                LArray.append(lsplit)

                if len(lsplit) < 4:
                    isSingleGas = True
                    break
                i += 1

        if isSingleGas:
            pass
        else:
            self.Name = LArray[0][0]
            self.Sticking = np.array(
                [float(LArray[1][1]), float(LArray[1][2]), float(LArray[1][3]), float(LArray[1][4])])
            self.EtaI = np.array(
                [[float(LArray[2][1]), float(LArray[2][2]), float(LArray[2][3]), float(LArray[2][4])],
                 [float(LArray[3][1]), float(LArray[3][2]), float(LArray[3][3]), float(LArray[3][4])],
                 [float(LArray[4][1]), float(LArray[4][2]), float(LArray[4][3]), float(LArray[4][4])],
                 [float(LArray[5][1]), float(LArray[5][2]), float(LArray[5][3]), float(LArray[5][4])]])

            self.EtaE = np.array(
                [float(LArray[6][1]), float(LArray[6][2]), float(LArray[6][3]), float(LArray[6][4])])
            self.EtaPh = np.array(
                [float(LArray[7][1]), float(LArray[7][2]), float(LArray[7][3]), float(LArray[7][4])])
            self.OutGassing = np.array(
                [float(LArray[9][1]), float(LArray[9][2]), float(LArray[9][3]), float(LArray[9][4])]       # Shouldn't divide by T?!!!!!!!
                ) * 1.0e3 / 1.3806488e-23  # molecules/s
            self.LinearPumping = np.array(
                [float(LArray[8][1]), float(LArray[8][2]), float(LArray[8][3]), float(LArray[8][4])]
                ) * 1.e-3  # m3/s
            self.esdLoaded = False
            self.seyLoaded = False
            self.LoadESDCurve()
            self.LoadCryoSticking()
            #self.LoadSEYCurve()

    def LoadESDCurve(self):
        """
            If esdLoaded is True, loads the ESD vs. electron dose curve for the Material.
        """

        ESDFolder = "/".join(self.File.split("/")[:-2]) + "/ESD/"
        print ESDFolder

        print "os.listdir(ESDFolder)", os.listdir(ESDFolder)
        print self.Name, "ESD_" + self.Name + ".csv" in os.listdir(ESDFolder)
        if "ESD_" + self.Name + ".csv" in os.listdir(ESDFolder):
            self.EsdCurve = ESD(ESDFolder + "ESD_" + self.Name + ".csv")
            self.esdLoaded =True
            print "ESD curve uploaded successfully"
        else:
            self.EsdCurve = None
            self.esdLoaded = False
            print " No ESD curve for this Material"

    def LoadSEYCurve(self,tdiFile):
        """
            If seyLoaded is True, loads the SEY vs. electron dose curve for the Material.
        """

        SEYFolder = "/".join(self.File.split("/")[:-2]) + "/SEY/"
        print SEYFolder
        print "os.listdir(SEYFolder)", os.listdir(SEYFolder)
        print self.Name, "SEY_" + self.Name + ".csv" in os.listdir(SEYFolder)
        if "SEY_" + self.Name + ".csv" in os.listdir(SEYFolder):
            self.SeyCurve = TDIS(SEYFolder + "SEY_" + self.Name + ".csv",tdiFile)
            self.seyLoaded = True
            print "SEY curve uploaded successfully"
        else:
            self.SeyCurve = None
            self.seyLoaded = False
            print " No SEY curve for this Material"

    def LoadCryoSticking(self):
        """
        Loads the cryogenic behavior of the sticking coefficient
        """    
    
        self.CryoSticking = []
        CryoFolder = "/".join(self.File.split("/")[:-2]) + "/Cryogenics/"
        if self.Name in os.listdir(CryoFolder):
            f = open(CryoFolder + self.Name + ".csv")
            lines = f.readlines()
            f.close()
        else:
            f = open(CryoFolder + "Default.csv" )
            lines = f.readlines()
            f.close()

        i = 0
        while i < len(lines):
            t =  [l for l in lines[i].strip("\n").split(",")[1:] if l != ""]
            i += 1
            alpha = [l for l in lines[i].strip("\n").split(",")[1:] if l != ""]
            i +=1
            if len(t) == 1:
                self.CryoSticking.append([float(t[0]), [], float(t[-1])])
            else:
                self.CryoSticking.append([float(t[0]),[[float(temp) for temp in  t] , [float(alph) for alph in alpha]],float(t[-1])])

    def GetSticking(self,T):
        """
        Gets the sticking coefficient of a material as a function of the temperature.
        @param T: (float) Temperature
        @return: alpha (array). Sticking coefficient at temperature T for the different relevant gases
        """
        alpha = []
        for i in range(4):
            if T <= self.CryoSticking[i][0]:
                alpha.append(1.)
            elif T >= self.CryoSticking[i][2]:
                alpha.append(self.Sticking[i])
            else:
                alpha.append(np.interp(T, self.CryoSticking[i][1][0],self.CryoSticking[i][1][1] ))
        return alpha


    def showAll_Material(self,MaterialsArray):
        """
        """
        for M in MaterialsArray:
            dir_Pumps = self.PumpFolder + 'P0' + '.csv'
            f = open(dir_Pumps, 'w+')
            f.write('P0' + ',' + '\n')
            for i in range(4):
                f.write(caption_Pump[i] + ',' + str(0) + '\n')
            f.close()
