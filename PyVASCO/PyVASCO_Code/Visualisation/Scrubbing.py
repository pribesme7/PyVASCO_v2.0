from Components import ESD
from  Config import Config
from Computation.Core2 import GetSegments, Calculate
import numpy as np


def runSimulation(Current,eDoseRange):
    """
     Computes the pressure profile for a given geometry and for a fix collection of rising received electron dose values,
     taking into account the reduction of the ESD as a function of the dose for those materials with a specified ESD vs.
     dose curve.

     Parameters
     ==========
        @param Current: (float) Proton beam current (in A)
    """

    Config.useESDCurve = True
    Config.uploadElectronFluxFromSEY = False
    listDensity = []
    # Run npoints simulations with equi-spatiated doses

    for eDose in eDoseRange:

        Config.eDose = eDose
        print "eDose updated to ", Config.eDose
        print "Config.useESDCurve", Config.useESDCurve
        Segments, EndPump, EndSource, DivisionList, GeometryParameters = GetSegments(Config.DataFile)

        # total_length needs to be caluclated for positioning the object in the scene
        total_length = 0
        listDensity.append(Calculate(Segments, EndPump, EndSource, Current=Current))


    Config.useESDCurve = False
    return listDensity








