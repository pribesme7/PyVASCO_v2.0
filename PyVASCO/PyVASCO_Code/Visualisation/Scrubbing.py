from Components import ESD
from  Config import Config
from Computation.Core2 import GetSegments, Calculate
import numpy as np


def runSimulation(Current,eDoseRange):
    """
     Computes the pressure profile for a given geometry and for a fix collection of rising received electron dose values,
     taking into account the reduction of the ESD as a function of the dose for those materials with a specified ESD vs.
     dose curve.

     Parameters:
     ----------
    :param Current: (float) Proton beam current (in A)
    """

    Config.useESDCurve = True
    Config.uploadElectronFluxFromSEY = False
    listDensity = []
    # Run npoints simulations with equi-spatiated doses
    #eDoseRange = np.array([1e13,1e14,1e15,1e16,1e17,1e18])
    for eDose in eDoseRange:

        Config.eDose = eDose
        print "eDose updated to ", Config.eDose
        print "Config.useESDCurve", Config.useESDCurve
        Segments, EndPump, EndSource, DivisionList, GeometryParameters = GetSegments(Config.DataFile)

        # total_length needs to be caluclated for positioning the object in the scene
        total_length = 0
        listDensity.append(Calculate(Segments, EndPump, EndSource, Current=Current))
        '''
        try:
            GeometryParameters[0]
        except TypeError:
            QMessageBox.warning(self, "ERROR in Input Parameters",
                                "Please define the Input parameter correctly! Did you set the parameter name in the file? Do you have to change the input folder?",
                                QMessageBox.Ok)

        eDoseRange, listDensity = Scrubbing.runSimulation(self.scrubbingSpinBox.value(), Segments, EndPump, EndSource,
                                                          current_set)
        '''

    Config.useESDCurve = False
    return listDensity








