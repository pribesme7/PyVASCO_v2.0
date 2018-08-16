import numpy as np
import math
import matplotlib.pyplot as plt

class ESD:
    """
    Parameters:
    ----------
    **name** (str): Name of the directory containing a curve ESD vs. electron dose

    Attributes:
    -----------
    **dataFrame** (list) : \n
    **EsdH2** (float): Electron Stimulated Desorption yield for H2 at a given electron dose. \n
    **EsdCH4** (float): Electron Stimulated Desorption yield for CH4 at a given electron dose. \n
    **EsdCO** (float): Electron Stimulated Desorption yield for CO at a given electron dose. \n
    **EsdCO2** (float): Electron Stimulated Desorption yield for CO2 at a given electron dose. \n

    Methods:
    -------
    * interpolate( (float) edose)
    * read_csv ((str) name)


    """
    def __init__(self,name):
        self.dataFrame = self.read_csv(name)

    def interpolate(self,edose):
        """
        Given a value of electron dose received on the surface of the studied material, computes the ESD corresponding
        to that dose for H2, CH4, CO and CO2.\n

        Parameters:
        ----------
        :param edose: (float) Received electron dose (in e-/cm^2)
        """
        i = np.argmin(abs(np.array(self.dataFrame["DOSe/cm2"]) - edose))

        if self.dataFrame["DOSe/cm2"][i] == edose:
            self.EsdH2 = self.dataFrame["H2"][i]
            self.EsdCH4 = self.dataFrame["CH4"][i]
            self.EsdCO = self.dataFrame["CO"][i]
            self.EsdCO2 = self.dataFrame["CO2"][i]

        else:
            #if self.dataFrame["DOSe/cm2"][i] < edose:
            #    j = i-1
            #else:
            #    j = i
            xp = np.log(self.dataFrame["DOSe/cm2"])
            '''
            self.EsdH2 = (self.dataFrame.H2[j+1] - self.dataFrame.H2[j])/(self.dataFrame["DOSe/cm2"][j+1] -
                          self.dataFrame["DOSe/cm2"][j]) * (edose - self.dataFrame["DOSe/cm2"][j] ) + self.dataFrame.H2[j]
            self.EsdCH4 = (self.dataFrame.CH4[j+1] - self.dataFrame.CH4[j]) / (self.dataFrame["DOSe/cm2"][j+1] -
                           self.dataFrame["DOSe/cm2"][j]) * (edose - self.dataFrame["DOSe/cm2"][j]) + self.dataFrame.CH4[j]
            self.EsdCO = (self.dataFrame.CO[j+1] - self.dataFrame.CO[j]) / (self.dataFrame["DOSe/cm2"][j+1] -
                          self.dataFrame["DOSe/cm2"][j]) * (edose - self.dataFrame["DOSe/cm2"][j]) + self.dataFrame.CO[j]
            self.EsdCO2 = (self.dataFrame.CO2[j+1] - self.dataFrame.CO2[j]) / (self.dataFrame["DOSe/cm2"][j+1] -
                           self.dataFrame["DOSe/cm2"][j]) * (edose - self.dataFrame["DOSe/cm2"][j]) + self.dataFrame.CO2[j]
            '''

            self.EsdH2 = math.e**np.interp(np.log(edose),xp,np.log(self.dataFrame["H2"]))
            self.EsdCH4 = math.e**np.interp(np.log(edose),xp,np.log(self.dataFrame["CH4"]))
            self.EsdCO = math.e**np.interp(np.log(edose),xp,np.log(self.dataFrame["CO"]))
            self.EsdCO2 = math.e**np.interp(np.log(edose),xp,np.log(self.dataFrame["CO2"]))

        self.EtaE = np.array([self.EsdH2, self.EsdCH4, self.EsdCO, self.EsdCO2])
        #plt.plot(self.dataFrame["DOSe/cm2"], self.dataFrame["H2"], label="H2")
        #plt.plot(self.dataFrame["DOSe/cm2"], self.dataFrame["CH4"], label="CH4")
        #plt.plot(self.dataFrame["DOSe/cm2"], self.dataFrame["CO"], label="CO")
        #plt.plot(self.dataFrame["DOSe/cm2"], self.dataFrame["CO2"], label="CO2")
        #plt.scatter([edose] * 4, [self.EsdH2, self.EsdCH4, self.EsdCO, self.EsdCO2],c="black")
        #plt.xscale("log")
        #plt.yscale("log")
        #plt.show()


    def read_csv(self,NFile,headers =True,delimiter=","):
        """
        Reads and parses the input file NFile containing the ESD vs. electron dose for H2, CH4, CO and CO2. \n

        Parameters:
        ----------

        :param NFile: (str) Name of the directory containing a curve ESD vs. electron dose
        :param headers: (optional, bool) If True, the names of the columns are kept as the keys of the output dictionary
        :param delimiter: (optional, str) Delimiter used to separate the data in NFile

        Returns:
        -------
        :return data: If headers is True --> dict containing the names of the columns as keys. If headers is False --> list
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


'''
esd = ESD(1e19)
print esd.EtaE
esd.dataFrame.plot(x="DOSe/cm2",y="H2",logx=True,logy=True)
plt.scatter(1e19,esd.EtaE[0])
plt.show()
'''