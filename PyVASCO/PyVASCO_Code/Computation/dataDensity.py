import numpy as np


class DensityClass:
    """
    
    @param x: (list) X-coordinates of a density/pressure profile
    @param listH2: (list) Density/pressure of hydrogen (H2) in the positions x
    @param listCH4: (list) Density/pressure of methane (CH4) in the positions x
    @param listCO: (list) Density/pressure of carbon monoxide (CO) in the positions x
    @param listCO2: (list) Density/pressure of carbon dioxide (CO2) in the positions x
    @param listTemp: (list) List of the temperature in the positions x
    @param boolDensity: (bool) If True --> Density, else: Pressure

    Attributes
    ==========
        **X** (list): X-coordinates of a density/pressure profile
        **H2** (list): Density/pressure of hydrogen (H2) in the positions x
        **CH4** (list):Density/pressure of methane (CH4) in the positions x
        **CO** (list): Density/pressure of carbon monoxide (CO) in the positions x
        **CO2** (list): (list) Density/pressure of carbon dioxide (CO2) in the positions x
        **VapPressure** (list): List of the temperature in the positions x

    Methods
    =======
        * transformation ((list) sensitivityFactor) :returns: (DensityClass)
        * setDensity ((DensityClass) DensityClass)
        * setTemperatureProfile((list) templist)
        * total()

    """
    def __init__(self, x = [], listH2 = [], listCH4 = [], listCO = [], listCO2 = [],listTemp=[], boolDensity = True):
        self.density = boolDensity # True  =  Density, False = Pressure
        self.X = x
        self.H2 = listH2
        self.CH4 = listCH4
        self.CO = listCO
        self.CO2 = listCO2
        self.Temperature = listTemp
        self.SensitivityFactor = [1.,1.,1.,1.]

    def transformation(self):
        """
        Transforms density [particles/m3] to pressure [mbar] and pressure to density with a given sensitivity factor for
         each considered gas specie (H2,CH4,CO and CO2).

        @param sensitivityFactor: (optional, list) Sensitivity factors to use in the transformation between density and
         pressure. Default value is [1,1,1,1]

        """
        # transforms density [particles/m3] to pressure [bar] and pressure to density
        # densityArray = [h2Array, ch4array, coArray, co2Array] 

        factor = 1.3806488e-23* 0.01
        tempfactor = self.Temperature

        if self.density == False: 
            factor = 1/factor
            tempfactor = 1./np.array(self.Temperature)
            self.density = True
        else: self.density = False
        print "len(tempfactor) = ", len(tempfactor)
        print "zip(self.H2,tempfactor)[0:10]",zip(self.H2,tempfactor)
        self.H2 = [x * T * factor for x, T in zip(self.H2,tempfactor)]
        self.CH4 = [x * T * factor for x, T in zip(self.CH4,tempfactor)]
        self.CO = [x * T * factor for x, T in zip(self.CO,tempfactor)]
        self.CO2 = [x * T * factor for x, T in zip(self.CO2,tempfactor)]
        #self.density  =  not self.density
        return self
       
    def setDensity(self, densityObject):
        """
        Copies the values of the attributes density, H2, CH4,CO and CO2 of an input DensityClass object.

        @param densityObject: (DensityClass) Object to copy
        """
        self.density = densityObject.density # True = Density, False = Pressure
        self.X = densityObject.X
        self.H2 = densityObject.H2
        self.CH4 = densityObject.CH4
        self.CO = densityObject.CO
        self.CO2 = densityObject.CO2
        self.SensitivityFactor = self.setSensitivityFactor(densityObject.SensitivityFactor)

    def setTemperatureProfile(self,tempList):
        """
       Sets the temperature profile.

        @param tempList: (list) VapPressure profile. Must be defined in the positions given by X.
        """
        self.Temperature = tempList

    def setSensitivityFactor(self,SensitivityFactor):
        self.SensitivityFactor = SensitivityFactor

    def SensitivityTotal(self):
        """
        Computes the total pressure for  given sensitivity factors.

        """
        if self.density is True:
            # Transform to pressure
            self.transformation()
        else:
            pass

        a = [x * self.SensitivityFactor[0] for x in self.H2]
        b = [x * self.SensitivityFactor[1] for x in self.CH4]
        c = [x * self.SensitivityFactor[2] for x in self.CO]
        d = [x * self.SensitivityFactor[3] for x in self.CO2]
        return map(np.sum, zip(a, b, c, d))


    def total(self):
        """
        Computes the total molecular density or the total pressure as defined by Dalton's law.\n

        """
        sensitivityFactor = [0.416666,1.4285,1.1111,1.4285 ]
        a = [x  for x in self.H2]
        b = [x  for x in self.CH4]
        c = [x  for x in self.CO]
        d = [x  for x in self.CO2]

        return map(np.sum, zip(a, b, c, d))




Density = DensityClass()
