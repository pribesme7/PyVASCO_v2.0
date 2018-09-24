import numpy as np


class Gassource:
    """
    Parameters
    ==========
    @param File: (str) Name of the directory containing a gas source.

    Attributes
    ==========
    B{Name} (str): Name of the gs source, typically G + Number \n
    B{GasRelease} (numpy.array): Localized gas source [H2,CH4,CO,CO2]
    """
    Name = ''
    GasRelease = []

    def __init__(self, File):
        print('Gassource constructor')
        LArray = []
        with open(File) as f:
            for line in f.readlines():
                lsplit = line.strip("\n").split(',')
                LArray.append(lsplit)
        self.Name = LArray[0][0].strip(" ")
        self.GasRelease = np.array(
            [float(LArray[1][1]), float(LArray[2][1]),
             float(LArray[3][1]), float(LArray[4][1])]
            ) * 1.0e-1 / 1.3806488e-23/293.15
