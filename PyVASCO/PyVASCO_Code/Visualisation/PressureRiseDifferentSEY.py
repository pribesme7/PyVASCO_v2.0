from Config import Config
from Computation.Core2 import GetSegments, Calculate
import numpy as np
import os
import pandas as pd
import pickle



def runTDISSimulation(Current):
    """
    Simulation for the TDIS. See user manual for more details. 
    
    Description
    ===========
    
    Computes the maximum pressure as a function of the half-gap, for a given Beam current, and for a fix collection of
    rising received electron dose values, taking into account the reduction of the ESD as a function of the dose and the
    decrease of the Electron flux coming from Electron cloud on the walls due to the reduction of the SEY as a function
    of the received electron dose. This simulation assumes that the SEY is homogeneous in the TDIS chamber.\n

    Parameters
    ==========
    
    @param Current: (float) Proton beam current
    """
    Config.useESDCurve = True
    Config.uploadElectronFluxFromSEY = True
    print("Config.uploadElectronFluxFromSEY", Config.uploadElectronFluxFromSEY)
    halfGapRange = [4,6,8,10,15,20,25,30,35,40,45,50] 
    eDoseRange = np.array([9.0e15,1.9e16,4e16,9e16,3.7e17,6.24e18])                                  
    # eDose range selected in order to obtain SEYs close to 1.6,1.5,1.4,1.3,1.2 and 1.1
    data = {}
    for eDose in eDoseRange:
        Config.eDose = eDose
        listMaxPressure = []
        listSey = []
        for g in halfGapRange:
            Config.halfGap = g
            Segments, EndPump, EndSource, DivisionList, GeometryParameters = GetSegments(Config.TDISFile)
            listSey.append(Config.currentSey)
            PressureProfile = Calculate(Segments, EndPump, EndSource, Current=Current).transformation()
            listMaxPressure.append(max(PressureProfile.total()))

        data["SEY " + str(max(listSey))] = np.array(listMaxPressure)
    Config.uploadElectronFluxFromSEY = False
    Config.useESDCurve = False
    return halfGapRange,data


def runTDISSimulation_nonHomogeneousSEY(Current):
    """
    Simulation for the TDIS. See user manual for more details. \n
    
    Description
    ===========
    Computes the maximum pressure as a function of the half-gap, for a given Beam current, for the non-homogeneous
    SEY distributions in the TDIS chambers (described in Config). If a curve of ESD as a function of dose is available for
    the material of the beam screen of the TDIS chamber, the ESD corresponding to the SEY considered in the beam screen
    is used in the computation of the pressure profile. \n

     Parameters
     ==========
    @param Current: (float) Proton beam current
    """
    Config.TotalOutgassingForMaterials = ["BCu","BCu2"]
    for mat in [f for f in os.listdir(Config.MaterialFolder) if f.startswith("TDIS_BCu2") ]:
        Config.AddMaterial(mat)
    Config.AddMaterial("TDIS_NEG0.csv")



    Config.useESDCurve = False
    Config.uploadElectronFluxFromSEY = False
    halfGapRange = [4., 6., 8., 10., 15., 20., 25., 30., 35., 40., 45., 50.]

    Config.LoadTDISNonHomogeneous()
    print "Config.LoadTDISNonHomogeneous()"
    Data = {}

    for c in Config.CasesEFluxSEY.keys():
        listMaxPressure = []

        for g in halfGapRange:
           
            print "Half Gap = ", g , " mm"
            Config.halfGap = g
            Config.TDISFile =Config.DataFolder + "Input/TDIS_dynamic_HG" + str(int(g))+"mm_New.csv"
            Config.DataFile = Config.TDISFile

            Segments, EndPump, EndSource, DivisionList, GeometryParameters = GetSegments(Config.TDISFile)

            for Segment in Segments:

                print Segment.Name, Segment.Material
                print  " Config.CasesEFluxSEY[c][2]",Config.CasesEFluxSEY[c][2]
                print "Config.CasesEFluxSEY[c][3]" ,Config.CasesEFluxSEY[c][3]
                if np.any(np.array([Segment.Material +"_" in element for element in Config.CasesEFluxSEY[c][2]])):
                    sey = Config.CasesEFluxSEY[c][0]
                    print [element for element in Config.CasesEFluxSEY[c][2] if Segment.Material+"_" in element]
                    hg_vs_eCurrent = pd.read_csv([element for element in Config.CasesEFluxSEY[c][2] if Segment.Material+"_" in element][0])
                    
                    print "EFlux files", [element for element in Config.CasesEFluxSEY[c][2] if Segment.Material+"_" in element]
                    print "EFlux from ",[element for element in Config.CasesEFluxSEY[c][2] if Segment.Material+"_" in element][0]

                    print np.array(hg_vs_eCurrent["Half Gap [mm]"]), g, np.array(hg_vs_eCurrent.ix[:,1])
                    Segment.ElectronFlux = np.interp(g,np.array(hg_vs_eCurrent["Half Gap [mm]"]), np.array(hg_vs_eCurrent.ix[:,1]))/Config.e/Segment.Length
                    print "in TDIS_non_homogeneous -->Segment.ElectronFlux",Segment.ElectronFlux

                    if sey == Config.CasesEFluxSEY[c][1][0] and os.path.isfile(Config.ESDFolder + "ESD_" +Segment.Material + ".csv"):  # Totally unscrubbed material --> Lowest eDose available
                        esd_vs_eDose = pd.read_csv(Config.ESDFolder + "ESD_" + Segment.Material + ".csv")
                        eDose = np.array(esd_vs_eDose.iloc[0])[0]
                        # Changing material properties in Config

                        Config.Materials[Segment.Material].EtaE= np.array(esd_vs_eDose.iloc[0])[1:]

                    elif sey == Config.CasesEFluxSEY[c][1][1] and os.path.isfile(Config.ESDFolder + "ESD_" +Segment.Material+ ".csv"): # Totally scrubed material --> Largest eDose available
                        esd_vs_eDose = pd.read_csv(Config.ESDFolder + "ESD_" + Segment.Material + ".csv")
                        eDose = np.array(esd_vs_eDose.iloc[-1])[0]
                        Config.Materials[Segment.Material].EtaE = np.array(esd_vs_eDose.iloc[-1])[1:]

                    else:
                        # Check if there are a SEY vs. eDose curve  and a ESD vs. eDose available for the material:
                            # YES: Find the eDose corresponding to the specified SEY. Find the corresponding ESD
                            # NO: Raise warning; don't modify ESD values of the material
                        if "SEY_" + Segment.Material+ ".csv" in Config.SEYFolder and "ESD_" +Segment.Material+ ".csv" in Config.ESDFolder:
                            sey_vs_eDose = pd.read_csv(Config.SEYFolder + "SEY_" + Segment.Material+ ".csv")
                            eDose = np.interp(sey_vs_eDose["SEY"], sey, sey_vs_eDose["DOSe/cm2"])
                            esd_vs_eDose = pd.read_csv(Config.ESDFolder + "ESD_" + Segment.Material + ".csv")
                            EtaEH2 =  np.interp(eDose,esd_vs_eDose["DOSe/cm2"],esd_vs_eDose.H2)
                            EtaECH4 = np.interp(eDose,esd_vs_eDose["DOSe/cm2"],esd_vs_eDose.CH4)
                            EtaECO = np.interp(eDose,esd_vs_eDose["DOSe/cm2"],esd_vs_eDose.CO)
                            EtaECO2 = np.interp(eDose,esd_vs_eDose["DOSe/cm2"],esd_vs_eDose.CO2)
                            Config.Materials[Segment.Material].EtaE = np.array([EtaEH2,EtaECH4,EtaECO,EtaECO2])
                        else:
                            raise Warning("Missing files for the simulation: ESD vs. eDose for material %s in directory "
                                          "%s  \n or SEY vs. eDose for material %s in directory %s \n" % (Segment.Material, Config.ESDFolder,Segment.Material,Config.SEYFolder))
                else:
                    continue
            print "To Calculate --> Segments[7].Material =",Segments[7].Material, "Config.Materials[Segments[7].Material].EtaE", Config.Materials[Segments[7].Material].EtaE, "Segments[7].ElectronFlux =", Segments[7].ElectronFlux
            
            PressureProfile = Calculate(Segments, EndPump, EndSource, Current=Current).transformation()

            pickle.dump([PressureProfile.H2,PressureProfile.CH4,PressureProfile.CO,PressureProfile.CO2],open("C:\Users\paribesm\PyCharmProjects\TDIS\Output\VASCO/pressure_" + str(g) + "mm_" + c + ".p","w"))

            infoMat = {}
            for Segment in Segments:
                infoMat[Segment.Name] = [Config.Materials[Segment.Material].EtaE,Segment.ElectronFlux]
            pickle.dump(infoMat,open("C:\Users\paribesm\PyCharmProjects\TDIS\Output\VASCO/info_materials" + str(g) +"_" + c +  ".p","w"))
            listMaxPressure.append(max(PressureProfile.total()))

        Data[Config.CasesEFluxSEY[c][3]] = listMaxPressure

    # Put back the original properties of all materials
    Config.LoadMaterials()
    return halfGapRange, Data


def ECLOUD_sim_Mat_to_csv(fname,outfname,tank="12"):
    """
    From an input MAT file containing as elements in the workspace the array labeled as 'half_gap' and the array labeled
    as 'current_T1T2' or 'current_T3', an output file of name 'outfname' in CSV format containing a column with the
    simulated Half-Gaps and another with the impinging electron current in the TDIS chambers (in A).

     Parameters
     ==========
    @param fname: (str) Name of the input MAT file
    @param outfname: (str) Name of the output CSV file
    @param tank: (str) '12' --> Tanks 1 and 2 or '3' -- > Tank 3 of the TDIS

    """
    import scipy.io as sio
    matData = sio.loadmat(fname)
    with open(outfname,"w") as f :
        if tank == "12":
            f.write("Half Gap [mm], ecurrent_T1T2 [A] \n")
            key = "current_T1T2"
        else:
            f.write("Half Gap [mm], ecurrent_T3 [A] \n")
            key = "current_T3"
        for g,i in zip(matData["half_gap"],matData[key]):
            f.write("%s,%s \n"%(str(g),str(i)))

