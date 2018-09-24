#import sys
#sys.path.append('../')
#from Config import Config as c
#from ESD import ESD
#from pandas import read_csv
import numpy as np
import os


class TDIS:
    """
    Properties
    ==========

    @var nfile: (str): Name of the file containing the half-gap vs. electron current curve. \n
    @var TDISFile:(str): Name of the file containing the description of the geometry of the TDIS. \n

    Attributes
    ===========
    B{nfile} (str): Name of the file containing the half-gap vs. electron current curve. \n
    B{TDISFile} (str): Name of the file containing the description of the geometry of the TDIS. \n
    B{daFrame} (dict): Dictionary containing the half-gap vs. electron current curve for different cases. \n
    B{sey} (float) : SEY in the TDIS (considering homogeneous SEY in the tanks). \n

    Methods
    =======
        - read_csv((float) NFile, (bool) headers, (str) delimiter)
        - seyFromDose((float) eDose)
        - setElectronCurrent()
    """
    def __init__(self,nfile,TDISFile):
        self.nFile = nfile
        self.TDISsFile = TDISFile
        self.dataFrame = self.read_csv(self.nFile)
        #self.isTDIS = isTDIS
        self.sey = 1.0

    def read_csv(self,NFile,headers =True,delimiter=","):
        """
         Reads and parses the input file NFile containing the ESD vs. electron dose for H2, CH4, CO and CO2. \n

        @param NFile: (str) Name of the directory containing a curve ESD vs. electron dose
        @param headers: (optional, bool) If True, the names of the columns are kept as the keys of the output dictionary
        @param delimiter: (optional, str) Delimiter used to separate the data in NFile


        @return: data. If headers is True --> dict containing the names of the columns as keys. If headers is False --> list
        """

        f = open(NFile)
        lines = f.readlines()
        f.close()

        if headers is True:
            data = {}
            headers =filter(None,lines[0].strip("\n").split(delimiter))
            for h in headers:
                data[h] = []

            for l in lines[1:]:
                l = filter(None,l.strip("\n").split(delimiter))
                for i,h in enumerate(headers):
                    data[h].append(float(l[i]))
            return data
        else:
            data = []
            for l in lines[1:]:
                l = filter(None, l.strip("\n").split(delimiter))
                data.append([float(l0) for l0 in l])
            return data

    def seyFromDose(self,eDose):
        """
        Computes the SEY of the TDIS tanks after a given received electron dose, considering that both  the surface of
        the chamber and the received electron flux are homogeneous.\n

        @param eDose: (float) : electron dose received on the surface of the TDIS (in e-/cm^2)
        """

        #print self.dataFrame
        #print np.array(self.dataFrame["DOSe/cm2"]) - eDose

        self.dataFrame = self.dataFrame[np.isfinite(self.dataFrame["DOSe/cm2"])]
        print self.dataFrame["DOSe/cm2"]
        i = np.argmin(abs(np.array(self.dataFrame["DOSe/cm2"]) - eDose))
        self.sey = self.dataFrame.SEY[i]
        print "For eDose", eDose, "determined SEY = ", self.sey
        self.setElectronCurrent()


    def setElectronCurrent(self):
        """
        Finds the closest SEY vs. half-gap curve to the SEY computed from the received electron dose.
        """
        # From the computed SEY, take the closest curve
        self.dataFrameCurrent = self.read_csv(self.TDISFile)
        #print self.dataFrameCurrent
        keys = self.dataFrameCurrent.keys()
        #print keys
        SeyValues = np.array([float(d.split("SEY ")[1]) for d in keys if "SEY" in d])
        print "In TDIS. SeyValues : ", SeyValues
        i = np.argmin(abs(SeyValues - self.sey))
        print "Closest value to", self.sey, "with known current is ", keys[i+1]
        self.sey = float(keys[i+1].split("SEY ")[-1])
        #print self.dataFrameCurrent[keys[i + 1]]
        self.eCurrent = np.array([self.dataFrameCurrent["Half-Gap [mm]"],self.dataFrameCurrent[keys[i + 1]]])




'''
f = "C:\Users\paribesm\PyCharmProjects\IdaVac\IdaVac\Data\Input\SEY\SEY_unbaked_copper.csv"
TDISf  =  "C:\Users\paribesm\PyCharmProjects\IdaVac\IdaVac\Data\Input\SEY\TDIS.csv"
TDIS = TDIS(f,TDISf)
print TDIS.dataFrame
TDIS.seyFromDose(1e18)
print TDIS.sey
print TDIS.eCurrent
'''

