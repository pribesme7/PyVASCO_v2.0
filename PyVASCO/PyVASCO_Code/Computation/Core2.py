from Computation import Core
from Computation import Plotter


from Config import Config

from Computation.dataDensity import  * 
from External_Input import External_Ph_Flux
import numpy as np
from os import listdir
from os.path import isfile, join

from Components.ESD import ESD
import math
from scipy.linalg import expm


def GetSegments(File=Config.DataFile):
    """
    Gets the segments conforming the simulated geometry, materials, outgassing, etc. from the specified input file. See the User guide for more details
    on the format of the input file.\n

    Parameters:
    ----------
    :param File: (str) : Input directory where the geometry, materials, outgassing, etc. for the simulation are defined.

    Returns:
    -------
    :Segments: (list) List of the segments conforming the geometry of the simulated system. \n
    :EndPump: (Pump) Pump located at the right side of the last segment \n
    :EndSource: (Gassource)  Gas source  located at the right side of the last segment. \n
    :DivisionsList: (list) List of integers ranging from 0 to the number of segments. \n
    :GeometryPlot: (list) List of tuples  specifying the length of each segment, its diameter, its material and its temperature.
    """
    print('GetSegments:', Config.DataFile, File)
    Segments = []

    LArray = []

    try:
        with open(File) as f:

            for line in f.readlines():
                line = line.rstrip()
                lsplit = line.split(',')
                LArray.append(lsplit)
    except IOError:
        print("Could not read in file", File)
        return 
    SegmentNames = LArray[0][1:]
    SegmentDiameters = LArray[1][1:]
    SegmentLengths = LArray[2][1:]
    SegmentTemperatures = LArray[3][1:]
    SegmentMaterials = LArray[4][1:]
    SegmentPumps = LArray[5][1:]
    SegmentGassources = LArray[6][1:]
    SegmentPhotonFlux = LArray[7][1:]
    SegmentElectronFlux = LArray[8][1:]
    #check if Materialfile is available for the simulation:
    availableMaterials = Config.Materials.keys()
    print "SegmentMaterials[:-1]", SegmentMaterials[:-1]
    for material in SegmentMaterials[:-1]:
        print material
        if not material in availableMaterials:
            e = material
            print "not material in availableMaterials"
            return  False , e,0,0 ,0


    NSeg = len(SegmentNames)
    DivisionsList = list(range(NSeg))

    GeometryPlot  =  zip(SegmentLengths,SegmentDiameters, SegmentMaterials,SegmentTemperatures)
    DivisionsPrint = 0
    DivisionsPrint2 = 0
    for i in range(NSeg):
        
        if SegmentDiameters[i] == '': 
            NSeg = i
            break
        Array = []
        Array.append(SegmentNames[i])
        Array.append(SegmentDiameters[i])
        Array.append(SegmentLengths[i])
        Array.append(SegmentTemperatures[i])
        Array.append(SegmentMaterials[i])
        Array.append(SegmentPumps[i])

        Array.append(SegmentGassources[i])
        Array.append(SegmentPhotonFlux[i])
        Array.append(SegmentElectronFlux[i])
        SegmentT = Segment(Array)
        try:
            MaxValue = (SegmentT.GetFundamentalSystem( Config.Materials[SegmentT.Material],SegmentT.Length)).max()
            Divisions = np.log2(MaxValue)/np.log2(Config.MaxValueLimit)

        except KeyError, e:
            print ' KeyError - reason "%s" ' % str(e)
            break
        except AttributeError:
            print('Singlegas')
            Divisions = 1
            
        
        try: Divisions2 = int(np.min([Config.MaximumDivisions,Divisions]))
        except:  Divisions2  =  Config.MaximumDivisions
        if Divisions2<1:
            Divisions2 = 1

        if NSeg < 10 :
            Divisions2 = int(Divisions2 * 16)
        if SegmentT.Is_Single_Gas:
            Divisions2 = 1.
        #else: Divisions2  =  int(Divisions2 * 8 * 8)
        #if i ==0: Divisions2 = 74
        DivisionsList[i] = Divisions2
        DivisionsPrint2 += Divisions2
        #print('Segment', i, 'is splitted in:', Divisions2 ,'elements', DivisionsPrint, DivisionsPrint2)
        DivisionsPrint = DivisionsPrint2
        Array[2] = 1.0 * float(SegmentLengths[i])/Divisions2

        if Divisions2 > 1: SegmentT = Segment(Array)
        Segments.append(SegmentT)
        #Splitting: creating new segments with zero pumping and zero gassource
        Array[5] = 'P0'
        Array[6] = 'G0'
        SegmentT = Segment(Array)
        for j in range(1,int(Divisions2)):  
            Segments.append(SegmentT)
    try:
        EndPump = Config.Pumps[SegmentPumps[-1].rstrip()]
        EndPump.SetNominalSpeed()
    except KeyError, e: 
        print ' KeyError - reason "%s" ' % str(e)
        return  False , e,0,0 ,0
    try: EndSource  =  np.array(Config.Gassources[SegmentGassources[-1].rstrip()].GasRelease)/SegmentT.Temperature 
    except KeyError, e: 
        print ' KeyError - reason "%s" ' % str(e)
        return False , e,0,0 ,0

        #Missing: Splitting
    print "Segments", Segments
    return Segments, EndPump, EndSource, DivisionsList, GeometryPlot



def SetPumpingSpeedforAvgPressure(Density,Segments,EndPump):
    xList = np.array(Density.X)
    TotalP = np.array(Density.transformation().total())
    x0Cum = 0
    xCum = 0
    for S in Segments:
        xCum += S.Length/2. + x0Cum
        AvgP = TotalP[(xList>=x0Cum)&(xList<=xCum)]
        AvgP = sum(AvgP)/len(AvgP)
        print AvgP
        S.Pump.SetPumpingSpeed(AvgP)
        x0Cum = xCum
        xCum = S.Length/2.

    AvgP = TotalP[(xList>=x0Cum)]
    AvgP = sum(AvgP) / len(AvgP)
    EndPump.SetPumpingSpeed(AvgP)

    return Segments, EndPump


class Segment:
    """
        Parameters:
        ----------
            **Array** (numpy.array) : Array containing the following properties of a segment: the length, the diameter,
            the temperature, the material, the name, the attached pumps, the gas source (if any) located at the end of the
            segment, the photon flux and the electron flux.

        Attributes:
        ----------
        **Diameter** (float): diameter of the segment, considered cylindrical (in m) \n
        **Length** (float): length of the segment (in m) \n
        **VapPressure** (float) : temperature of the segment (in K) \n
        **Material** (str): Name of the material of the segment \n
        **Name** (str): Name of the segment, typically S+Number
        **Pump** (str): Name of the pump attached to the start of the segment \n
        **Gassource** (str): Name of the gas source at the start of the segment \n
        **PhotonFlux** (float):  Homogeneous photon flux received in the segment (in photons/m/s) \n
        **ElectronFlux** (float): Homogeneous electron flux received in the segment (in electrons/m/s) \n
        **Is_Single_Gas** (bool): True if a single-gas model is used. \n


        Methods:
        -------
            * __init__()
            * isSinglegas((str) Material): returns: (bool)
            * PrintMatrix2()
            * GetMatrices((Material) Material, (float) Current ): returns: (ndarray), (ndarray), (float), (ndarray),
            (ndarray), (ndarray) \n
            * GetFundamentalSystem((Material) Material, (float) x): returns: (ndarray)
            * GetLength():  returns: (float)
            * GetDiameter(): returns: (float)
            * UploadElectronFlux((Material) Material, (float) HalfGap)
        """

    Diameter = 0
    Length = 0
    Temperature = 0

    Material = ''
    Pump = ''
    Gassource = ''

    PhotonFlux = 0
    ElectronFlux = 0

    Name = ''

    def __init__(self,Array): #Array contains only data about one segment
        self.Diameter = float(Array[1]) * 1.e-3
        self.Length = float(Array[2]) * 1.e-3
        self.Temperature = float(Array[3])
        self.Material = Array[4]
        self.Name = Array[0]
        self.Pump = Config.Pumps[Array[5]]
        self.Pump.SetNominalSpeed()
        self.Gassource = Array[6]
        self.PhotonFlux = float(Array[7])
        self.ElectronFlux = float(Array[8])
        self.Is_Single_Gas = self.isSinglegas(Config.Materials[self.Material])


    def isSinglegas(self, Material):
        """
        Checks if self (segment) is singlegas.  \n
        Parameters:
        ----------
        :param Material: (Material) Segment's material.\n

        Returns:
        -------
        :return: (bool) : Singlegas = True; Multigas = False
        """
        #checks if self (segment) is singlegas
        #Singlegas = True
        #Multigas = False
        for i in range(4):
            for j in range(4):
                if i != j and Material.EtaI[i][j] != 0 :
                    return False
        return True

    #def isRecursivePumpingSpeed(self):
    #    if len(Config.Pumps[self.Pump].PumpingCurve.keys()) > 1:
    #        self.RecursivePumpingSpeed = True
    #    else:
    #        self.RecursivePumpingSpeed = False


    def PrintMatrix2(A):
        """
          Prints on screen a formatted version of matrix A. \n
          Parameters:
          -----------
          :param A: (ndarray) Matrix to be printed

        """
        print('------------------------------')
        for i in range(0,  A.shape[0]):
            for j in range(0,  A.shape[1]):
                print("%10.2e\t"% (A[(i,  j)])), 
            print('')
        print('------------------------------')

    def GetMatrices(self, Material, outgassing = -1, Current = 0.5):
        """"
           Builds the Solving matrices. See User Guide for more information.

           Parameters:
           ----------
            :param Material: (Material): Segment's material \n
            :param Current: (float) : proton beam current \n

           Returns:
           -------
           :param B: (ndarray) :
           :param c: (ndarray) :
           :param Length: (float):
           :param Pumping: (ndarray):
           :param OutgassingLocal: (ndarray):
           :param A: (ndarray): Matrix containing the specific conductances for the main gasses present in an UHV system (H2, CH4, CO, CO2). The default gases can be modified changing the masses of the array 'Masses' in Config
               """
        print('Segment-GetMatrices')
        # Material needs to be set as input parameter, because it needs the function "load materials" to access the material properties. 
        Surface = math.pi * self.Diameter
        VelocityMean = np.sqrt(8 * Config.kB * self.Temperature/math.pi/Config.Mass)
        CrossSection = math.pi * (self.Diameter/2.)**2

        BeamCurrent = Current
        Pumping = self.Pump.Name
        OutgasingLocal = self.Gassource

        print "Mass =", Config.Mass

        #self.A = (Surface * 2 * np.sqrt(Surface/math.pi))/3 * np.sqrt(math.pi * Config.kB * self.Temperature/2/Config.Mass) #Area * Diffusivity,Diff = pi/6 * R * sqrt((8 * kb * T)/(pi * m)) --> Ida's version. Doesn't match with the definition of the specifinc conductance in her thesis!!!
        self.A = math.pi*self.Diameter**3/12.*VelocityMean   # Exactly as in VASCO!
        print "Conductance for segment ", self.Name, "is", self.A, "m**4 / s  "
        # print self.S,self.Name,T,Current,Energy,ECLOUD,ECLOUDBoost
        # print Perimeter * self.Material.OutGassing,PhFlux,ECLOUDD

        # Deriving from multigas appropriate eta_i for single gas 
        #print 'etai = ',  np.dot(Material.EtaI, Config.CrossSection)/ Config.CrossSection

        B = BeamCurrent/Config.e * np.dot(Material.EtaI, np.diag(Config.CrossSection)) - np.diag(Surface/4. * VelocityMean * (Material.Sticking) + Material.LinearPumping)
        print("MatrixB", B)
        #B = 0 * np.identity(4)
        #Check ill-conditioned segments
        #if np.max(np.diag(B)) > 0:
            #print 'matrix B',  np.diag(B)
        #print 'B', B

        #OutGassingRatio = np.exp(-Config.EnergyOutgassing/(Config.kB * T))/np.exp(-Config.EnergyOutgassing/(Config.kB * Config.RoomTemperature))
        #if OutGassingRatio<1:
        #	print OutGassingRatio

        #c = Surface * Material.OutGassing + self.PhotonFlux * Material.EtaPh + self.ElectronFlux * Material.EtaE

        print "In Core2, line 208. Config.useESDCurve",Config.useESDCurve
        #if Material.Name == "BCu" or Material.Name == "BCu2":
        #    with open(Config.logFile, "a") as f:
        #        l = "Segment " + str(self.Name) + "made of" +str(self.Material) + " with EFlux " + str(self.ElectronFlux) + " \n"
        #        line = "For material" + Material.Name + " Updata ESD ? :" + str(Config.useESDCurve) + '. Parameters before update : \n'
        #        line2 = "EtaE : ["+ ",".join([str(eta) for eta in Material.EtaE]) + "] Electron Flux :" + str(self.ElectronFlux) + "\n"
        #        f.write(l+line + line2)
        #if self.Name == "S8":
        #    line = "For material" + Material.Name + " Updata ESD ? :" + str(
        #        Config.useESDCurve) + '. Parameters before update : \n'
        #    line2 = "EtaE : [" + ",".join([str(eta) for eta in Material.EtaE]) + "] Electron Flux :" + str(
        #        self.ElectronFlux) + "\n"
        #    print line
        #    print line2
        #    print str(self.ElectronFlux)
        #    return None

        if Config.useESDCurve is True:
            print "Config.eDose", Config.eDose
            print " Material.esdLoaded", Material.esdLoaded

            if Material.esdLoaded is False:
                Material.LoadESDCurve()
            try:
                Material.EsdCurve.interpolate(Config.eDose)
                Material.EtaE = Material.EsdCurve.EtaE
                print "Material.EsdCurve.interpolate(Config.eDose)"
                print "Material.EsdCurve.EtaE", Material.EsdCurve.EtaE
            except:
                #raise Warning("Material doesn't have an ESD curve associated!!! ")
                print "Material doesn't have an ESD curve associated!!! "
                pass

            print("Material EtaE updated to ", Material.EtaE )
        else: pass

        print "In Core2, line 228. SEY upload"
        if Config.uploadElectronFluxFromSEY is True:
            # The correspondif file containing TDI/TDIS information is loaded
            Material.LoadSEYCurve(Config.TDISFile)
            if Material.SeyCurve is not None:
                Material.SeyCurve.seyFromDose(Config.eDose)

                print "For material ", Material.Name, "eDose = ", Config.eDose, "EtaE = ", Material.EtaE, ""
                Config.currentSey = Material.SeyCurve.sey
                # Compute here the new ElectronFlux from the e- current associated with SEY
                self.UploadElectronFlux(Material, Config.halfGap)
                #if Material.Name == "M50" or Material.Name == "M52":
                #    with open(Config.logFile, "a") as f:
                #        f.write("For eDose :" + str(Config.eDose) + " ESD updated to [" + ",".join([str(eta) for eta in Material.EtaE]) + "]"
                #                + "SEY updated to " + str(Material.SeyCurve.sey) + " and EFlux set to " + str(self.ElectronFlux)
                #                + "\n")
            else:
                print "Material doesn't have an SEY curve associated!!!"
                pass

        else:
            print "Config.uploadElectronFluxFromSEY is False. Not changing value"

        if self.Temperature < 15:
            #cryo_pumping = 1.e10
            #Config.nEq/self.Temperature
            cryo_pumping = []
            i = 0
            labels = ["H2", "CH4", "CO", "CO2"]
            for gas in Config.nEq:
                nEq = gas[1][np.argmin(abs(gas[0] - self.Temperature))] / self.Temperature

                print "CryoSurface --> T =",self.Temperature, "nEq =", nEq, " for ", labels[i]
                i +=1
                cryo_pumping.append(nEq)

            cryo_pumping = np.array(cryo_pumping)
        else:   cryo_pumping = 0.

        if np.any(np.array(Config.TotalOutgassingForMaterials) ==self.Material):
            print "self.Material",self.Material
            print "Config.TotalOutgassingForMaterials", Config.TotalOutgassingForMaterials
            print "Material.OutGassing",Material.OutGassing
            TotalOutgassing = Material.OutGassing /1e4/self.Temperature  # molecules/s
            print "TotalOutgassing", TotalOutgassing

        else:
            print "self.Material", self.Material
            print "Config.TotalOutgassingForMaterials", Config.TotalOutgassingForMaterials
            print "Material.OutGassing", Material.OutGassing, " Surface", Surface
            TotalOutgassing = Material.OutGassing * Surface/self.Temperature  # molecules/s
            print "TotalOutgassing", TotalOutgassing
        c = cryo_pumping*Surface * VelocityMean/4. * Material.Sticking + self.ElectronFlux * Material.EtaE + self.PhotonFlux * Material.EtaPh + TotalOutgassing

        print 'c: ', c

        ##############Singlegas:
        #if self.isSinglegas(Material):

        for i in range(4):
            for j in range(4):
                if i != j and B[i][j] != 0:
                    self.M = np.bmat([[np.zeros((4, 4)), np.identity(4)], [-np.dot(np.diag(np.divide(np.ones(4), self.A)), B), np.zeros((4, 4))]])
                    self.b = np.bmat([np.zeros(4), -np.dot(np.diag(np.divide(np.ones(4), self.A)), c)])
                    return self.M,np.transpose(self.b),self.Length, Pumping, OutgasingLocal, self.A

        print 'single'
        B = np.diag(B)
        return B, c, self.Length, Pumping, OutgasingLocal, self.A

        
        #ev = np.linalg.eigvals(self.M)
        #if np.max(ev.real) >  1:
            #print 'eigenval of M: ', ev.real

    def GetFundamentalSystem(self, Material ,x):
        """
           Eponenciates the matrix M in x

           Parameters:
           ----------
            :param Material: (Material): Segment's material \n
            :param x: (float) : Position [m]


           Returns:
           -------
            :param expMx: (ndarray): Exponentiation of matrix M in position x.
           """
        #if self.isSinglegas(Material):
            #return 1
        M,b,L,S,g,A = self.GetMatrices(Material)
        if np.size(M) == 64: # Multi gas
            fundamental = expm(M * x)
            return expm(M * x)
        else: 
            return 1 # Singel gas

    def GetLength(self):
        """
        Length of the segment. \n
        Returns:
        -------
        :param Length: (float) : length of the segment (in m).
        """
        return self.Length

    def GetDiameter(self):
        """
        Diameter of the segment. \n
        Returns:
        -------
        :param Diameter: (float) : Diameter of the segment (in m).
        """
        return self.Diameter

    """
    def changeLength(self,fraction):
        self.Lenght/=  (2 ** fraction)
    """

    def UploadElectronFlux(self, Material, halfGap):
        """
        Only used for the TDIS simulation. Gets the corresponding Electron flux for a specific half-gap. \n
        Parameters:
        ----------
        :param Material: (Material): Segment's material
        :param halfGap: (float) : Half-gap considered for the TDIS tanks. \n
        """

        print "UploadElectronFlux"
        halfGaps = Material.SeyCurve.eCurrent[0]
        print "Half Gaps", halfGaps
        print "eCurrent", Material.SeyCurve.eCurrent[1]
        i = np.argmin(abs(halfGaps-halfGap))
        print "For Half Gap", halfGaps[i]
        print "eCurrent :", Material.SeyCurve.eCurrent[1][i]
        with open(Config.logFile, "a") as f:
            f.write("for HG = " +  str(halfGap) + "eFlux = " +str( Material.SeyCurve.eCurrent[1][i]) ) #"eCurrent = " + str( Material.SeyCurve.eCurrent[1][i]) + "to divide by =" + str(self.Length) + "\n")

        #self.ElectronFlux = Material.SeyCurve.eCurrent[1][i]/(1000*Config.e*self.Length) # Current associated to SEY in mA
        self.ElectronFlux = Material.SeyCurve.eCurrent[1][i]


def UploadData(dir):
    """
    Loads a CSV file containing a pressure/density profile\n
    Parameters:
    ----------
    :param dir: (str) : Name of the directory to upload. \n
    Returns:
    -------
    :param Y1,Y2,Y3,Y4: (lists) : Uploaded data corresponding to the four first columns of the CSV file. \n
    """
    f = open(dir,'r')
    Array = []
    
    i = 0
    for line in f: # f.readlines():
        Array.append(line.split(','))    
    f.close()

    
    #Array  =  np.loadtxt(dir,float)

    X = []
    Y1 = []
    Y2 = []
    Y3 = []
    Y4 = []
    NRows = len(Array)
    for row in range(NRows): 
        Y1.append(float(Array[row][0]))
        Y2.append(float(Array[row][1]))
        Y3.append(float(Array[row][2]))
        Y4.append(float(Array[row][3])) #628
    return Y1, Y2, Y3, Y4

def UploadData2(dir):
    """
    Loads a CSV file containing a pressure/density profile\n
    Parameters:
    ----------
    :param dir: (str) : Name of the directory to upload. \n
    Returns:
    -------
    :param Y1,Y2,Y3,Y4: (lists) : Uploaded data corresponding to the two first columns of the CSV file. \n
    """

    f = open(dir,'r')
    Array = []
    
    i = 0
    for line in f: # f.readlines():
        Array.append(line.split(','))    
    f.close()

    
    #Array  =  np.loadtxt(dir,float)

    X = []
    Y1 = []
    NRows = len(Array)
    for row in range(NRows): 
        X.append(float(Array[row][0]))
        Y1.append(float(Array[row][1]))

    return X, Y1


'''
def IntegrandP(x, c, d):
	from math import sqrt
	return sqrt(1 + c *  * 2 * x *  * 2/d *  * 2/(d *  * 2-x *  * 2))

def CalculatePA(a,b,c,d):
	from math import sqrt,sin,cos,asin,pi
	from scipy.integrate import quad
	
	if a>c:
		a = c
	if b>d:
		b = d



	x1 = d * sqrt(1-a *  * 2/c *  * 2)
	x2 = b
	ax1 = asin(x1/d)
	ax2 = asin(x2/d)
	A1 = x1 * a
	A2 = c * d/2 * (ax2 + sin(ax2) * cos(ax2)-ax1-sin(ax1) * cos(ax1))
	A = 4 * (A1 + A2)
	
	

	P1 = x1
	P2,err = quad(IntegrandP, x1, x2, args = (c,d))
	P3 = c * sqrt(1-b *  * 2/d *  * 2)

	P = P1 + P2 + P3

	
	return P,A

def SplitSegment(SegmentO,SplitS):
	P = SegmentO.Perimeter
	A = SegmentO.Area
	S = SegmentO.S

	if SplitS<S[0] or SplitS>S[1]:
		print 'Spliting S ' + str(SplitS) + ' outside segment ' + str(S[0]) + '-' + str(S[0])
	else:
		PSplit = (P[0] * (SplitS-S[0]) + P[1] * (S[1]-SplitS))/(S[1]-S[0])
		ASplit = (A[0] * (SplitS-S[0]) + A[1] * (S[1]-SplitS))/(S[1]-S[0])

	NewSegment = Segment([PSplit,P[1]],[ASplit,A[1]],[SplitS,S[1]],SegmentO.Material,SegmentO.Name,Beam = SegmentO.Beam,Common = SegmentO.Common)
	SegmentO.Perimeter[1] = PSplit
	SegmentO.Area[1] = ASplit
	SegmentO.S[1] = SplitS
	return SegmentO, NewSegment

def DivideSegments(Segments):
	
	for Beam in range(0,2):
		SI = 0
		while SI<len(Segments[Beam]):
			Timer.Print('Segmenting ' + str(SI) + '/' + str(len(Segments[Beam])))
			MaxValue = (Segments[Beam][SI].GetFundamentalSystem(Materials[Segments[Beam][SI].Material], Segments[Beam][SI].Length())).max()	
			Divisions = np.log2(MaxValue)/np.log2(Config.MaxValueLimit)
			
			Divisions2 = int(np.min([Config.MaximumDivisions,Divisions]))
			if Divisions2<1:
				Divisions2 = 1
			Length0 = Segments[Beam][SI].Length()
			for j in range(1,Divisions2):  
				Old,New = SplitSegment(Segments[Beam][SI],Segments[Beam][SI].S[0] + Length0/Divisions2)
				Segments[Beam] = Segments[Beam][0:SI + 1] + [New] + Segments[Beam][SI + 1:]
				SI += 1
			SI += 1
	
	return Segments

def CheckMaxLength(Segments):
	
	for Beam in range(0,2):
		SI = 0
		while SI<len(Segments[Beam]):
			Timer.Print('Checking Max Length ' + str(SI) + '/' + str(len(Segments[Beam])))
			Ratio = int(Segments[Beam][SI].Length()/Config.MaxSegmentLength) 			
			Length0 = Segments[Beam][SI].Length()
			for j in range(1,Ratio):  
				
				Old,New = SplitSegment(Segments[Beam][SI],Segments[Beam][SI].S[0] + Length0/Ratio)
				Segments[Beam] = Segments[Beam][0:SI + 1] + [New] + Segments[Beam][SI + 1:]
				SI += 1
			SI += 1
			

	
	return Segments
			
def CleanZeroLength(Segments):
	NewSegments = [[],[]]

	for Beam in range(0,2):
		
		for OneSegment in Segments[Beam]:
			if OneSegment.Length()>0:
				NewSegments[Beam].append(OneSegment)		
	Segments = NewSegments
	return Segments
'''

def Calculate(Segments,EndPump, EndSource, Current = 0.5):
    """
    Computes the dynamic density profile of a given geometry considering beam induced effects. \n
    Parameters:
    -----------
    :param Segments: (list) : List of segments in the geometry \n
    :param EndPump: (Pump) : Pump located at the end of the last segment \n
    :param EndSource: (Gassource) : Gas source located at the end of the last segment \n
    :param Current: (float) : Proton beam current (in A).

    Returns:
    -------
    :param: density (DensityClass): Dynamic molecular density profile for H2,CH4,CO and CO2 in the considered geometry. \n
    """
    print('Calculate')
    print "Config.Materials =",Config.Materials["BCu2"].EtaE
    #Input is a list of segments
    #Matrices are created, equation system is solved
    #return: density object with values for the whole domain.

    #Materials = LoadMaterials()
    #Pumps = LoadPumps()
    #Gassources = LoadGassource()
    #Segments, EndPump, EndSource, Materials, Pumps, Gassources  = GetSegments()
    Solutions2 = []
    SegTemp = []
    for Beam in range(1,2):

        Ms = []
        bs = []
        Ls = []
        Ss = []
        gs = []
        As = []
        SI = 0
        index = 0
        index2 = 0
        index3 = 0
        if Config.OutgassingFile !=  ".":
            print('Config.OutgassingFile',Config.OutgassingFile)
            y1_outgas , y2_outgas,y3_outgas, y4_outgas  =  UploadData(Config.OutgassingFile)
  
            

        if Config.ElectronFile !=  ".":
            x_electron, y1_electron  =  UploadData2(Config.ElectronFile)

        
        if Config.PhotonFile !=  ".":
            LengthSegments = []
            for OneSegment in Segments:
                LengthSegments.append(OneSegment.Length)
            x_photon, y1_photon =  UploadData2(Config.PhotonFile)
            external_ph  =  External_Ph_Flux(LengthSegments, (x_photon, y1_photon))

            print ' len of photon list2: ', len(external_ph)


        for idSeg,OneSegment in enumerate(Segments):
            #defining external outgassing
            if Config.OutgassingFile !=  ".":
                #help = int(np.array(OneSegment.Length)/0.05)
                help = float(np.array(OneSegment.Length))
                print help
                outgassing  = []
                for o in [y1_outgas , y2_outgas, y3_outgas, y4_outgas]:
                    #print(o[index])
                    #print((np.sum(np.array(o[index:index + help]))/help)
                    #outgassing.append((np.sum(np.array(o[index:index + help]))/float(help)) * 1.0e3/1.3806488e-23)
                    print 'outgassing', (np.sum(np.array(o[index]))/help) * 1.0e3/1.3806488e-23
                    outgassing.append((np.sum(np.array(o[index]))/help) * 1.0e3/1.3806488e-23)
                    #outgassing.append((np.sum(np.array(o[index:index + help]))/help) * 1.0e3/1.3806488e-23)
                index += 1    
            else: outgassing  =  -1

            #defining external photon flux:

            if Config.PhotonFile !=  ".":
                OneSegment.PhotonFlux  =  external_ph[idSeg]


            if Config.ElectronFile !=  ".":
                help = int(np.array(OneSegment.Length)/0.005)
                OneSegment.ElectronFlux  =  np.sum(np.array(y1_electron[index3:index + help]))/help
                index3 += help       

            print "In Calculate --> Material =",OneSegment.Material
            print "In Calculate --> EFlux", OneSegment.ElectronFlux
            M,b,L, S,g, A  =  OneSegment.GetMatrices(Config.Materials[OneSegment.Material], outgassing, Current = Current)
            print idSeg
            #print('conductance', A[0])
            
            Ms.append(M)
            bs.append(b)
            Ls.append(L)
            SegTemp.append(OneSegment.Temperature)
            try: 
                Ss.append(Config.Pumps[S].Speed)
            except KeyError, e: 
                print ' KeyError - reason "%s" ' % str(e)
                return e             
            try: 
                gs.append(Config.Gassources[g].GasRelease/OneSegment.Temperature)

            except KeyError, e: 
                print ' KeyError - reason "%s" ' % str(e)
                return e
            As.append(A)

            #Timer.Print('Generating matrices Beam ' + str(Beam + 1) + ':' + str(SI) + '/' + str(len(Segments[Beam])))
            SI += 1

           
        #Ss.append(np.zeros((4,4)))
        #gs.append(np.zeros((4,1)))
        Ss.append(EndPump.Speed)
        gs.append(EndSource)

        Ps=[]
        if len(Ms) ==1:
            print 'single segment'
            Ps = Core.Solve_One_Segment_Singlegas(Ms,bs,Ls,Ss,gs,As)
        else:
            Ps = Core.Solve(Ms,bs,Ls,Ss,gs,As)
        print 'Ps', Ps
        if Ps  ==  []: return []

        xinit = 0.000000001
        print "Segment Temperatures =",SegTemp
        Solutions2,TempProfile = Plotter.GetSolutions(Ms,bs,Ls,Ps,SegTemp,Num = Config.NumPointsVacProfile,Xinit = xinit, As = As)
        density1 = DensityClass()
        density1.X =  []
        density1.H2 = []
        density1.CH4 = []
        density1.CO = []
        density1.CO2 = []
        density1.setTemperatureProfile([t[1] for t in TempProfile])
        for Point in Solutions2:
            density1.X.append(Point[0])
            density1.H2.append(Point[1][0,0])
            density1.CH4.append(Point[1][1,0])
            density1.CO.append(Point[1][2,0])
            density1.CO2.append(Point[1][3,0])       
    return density1

"""
def Geometry(Segments):
   
    print('Geometry')
    Length = []
    Diameter = []
    for OneSegment in Segments:
        Length.append(OneSegment.GetLength())
        Diameter.append(OneSegment.GetDiameter())
    return Length, Diameter

def GetAverage(x1, x2, Xs, Vs):
	N = len(Xs)
	if x1<Xs[0]:
		i1 = 0
	elif x1>Xs[N-1]:
		i1 = N-1
	else:
		i1a = 0
		i1b = N-1
		while i1b-i1a>1:
			if x1<Xs[(i1a + i1b)/2]:
				i1b = (i1a + i1b)/2
			else:
				i1a = (i1a + i1b)/2
		i1 = i1a
		
	if x2<Xs[0]:
		i2 = 0
	elif x2>Xs[N-1]:
		i2 = N-1
	else:
		i2a = 0
		i2b = N-1
		while i2b-i2a>1:			
			if x2 <= Xs[(i2a + i2b) / 2]:
				i2b = (i2a + i2b) / 2
			else:
				i2a = (i2a + i2b) / 2

		i2 = i2b
	
	
	XsN = list(Xs[i1:i2 + 1])
	VsN = list(Vs[i1:i2 + 1])
	

	if len(VsN) == 0:
		return Vs[i1]
	if len(VsN) == 1:
		return VsN[0]
	if x1<XsN[0]:
		
		XsN = [x1] + XsN
		VsN = [VsN[0]] + VsN
		
	elif x1>XsN[0]:
		
		if XsN[1]-XsN[0]!= 0:
			V = (VsN[1] * (x1-XsN[0]) + VsN[0] * (XsN[1]-x1))/(XsN[1]-XsN[0])
		else:
			V = VsN[0]
		XsN[0] = x1
		VsN[0] = V
		
	M = len(VsN)
	if x2>XsN[M-1]:	
		
		XsN = XsN + [x2]
		VsN = VsN + [VsN[M-1]]
		
	elif x2<XsN[M-1]:		
		if XsN[M-2] - XsN[M-1]!= 0:			
			V = 1. * (VsN[M-1] * (x2-XsN[M-2]) + VsN[M-2] * (XsN[M-1]-x2)) / (XsN[M-1] - XsN[M-2])			
		else:
			V = VsN[M-1]
		XsN[M-1] = x2
		VsN[M-1] = V

	
	Res = 0
	
	for i in range(len(XsN)-1):
		Res += (XsN[i + 1]-XsN[i]) * 0.5 * (VsN[i + 1] + VsN[i])
	if (XsN[len(XsN)-1]-XsN[0]) == 0:
		return VsN[0]
	else:
		return Res / (XsN[len(XsN)-1] - XsN[0])
"""