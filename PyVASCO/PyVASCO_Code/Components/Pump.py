import numpy as np
import os

class Pump():
    """
    Properties:
    ----------
     **File** (str): Name of the directory containing the pumping speeds for H2, CH4, CO and CO2 (in l/s).  \n

     Attributes:
     ----------
     **Name** (str): Name of the Pump, default P + Number
     **Speed** (numpy.array): Pumping speeds in m^3/s
    """

    Name = ''
    Speed = []

    def __init__(self, File):
        print('Pump Constructor')

        if os.path.isdir(File):
            self.LoadSpeedCurve(File)
            self.SetNominalSpeed()

        else:
            self.Name,self.Speed = self.LoadPump(File)
            self.PumpingCurve = {"Nominal":self.Speed}

    def SetPumpingSpeed(self,p):

        pressures = self.PumpingCurve.keys()
        try:
            pressures = sorted([float(k) for k in pressures if k != "Nominal"])
            print pressures
            key = min(pressures, key=lambda x: abs(x - p))
            self.Speed = self.PumpingCurve[self.eformat(key, 0, 1)]
        except:
            return


    def LoadSpeedCurve(self,File):
        self.Name = os.path.split(File)[-1]
        files = os.listdir(File)
        self.PumpingCurve = {}
        for f in files:
            p = f.split("_")[-1].split(".")[0]
            n,S = self.LoadPump(File+ "/" + f)
            self.PumpingCurve[p] = S


    def SetNominalSpeed(self):
        self.Speed = self.PumpingCurve["Nominal"]

    def LoadPump(self,File):
        LArray = []
        with open(File) as f:
            for line in f.readlines():
                lsplit = line.strip("\n").strip(" ").split(',')
                LArray.append(lsplit)
        Name = LArray[0][0]
        Speed = np.array(
            [float(LArray[1][1]), float(LArray[2][1]),
             float(LArray[3][1]), float(LArray[4][1])]
        ) * 1.e-3

        return Name, Speed

    def eformat(self,f, prec, exp_digits):
        s = "%.*e" % (prec, f)
        mantissa, exp = s.split('e')
        # add 1 to digits as 1 is taken by sign +/-
        return "%sE%+0*d" % (mantissa, exp_digits + 1, int(exp))