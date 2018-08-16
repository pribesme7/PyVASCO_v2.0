#import Config
#from Config import Config
# transforms the old input format to the new one, by adding as well missing materials/pumps/gassources to the corresponding folder
import sys
import os
import numpy as np
import copy
from os import listdir
from os.path import isfile, join
from Components import Material, Pump, Gassource
import Config
import unit 
#from Config import Config


def FileToArray(file,delimiter=','):

    print "FileToArray"

    try:
        f=open(file,'r')
        Array=[]
        i=0
        for line in f: # f.readlines():
            print i, filter(None,line.strip("\n").split(delimiter))
            Array.append(filter(None,line.strip("\n").split(delimiter)))

            i+=1 
            if i>48: break #without caption-line


        del Array[0] # deletes first row with captions (e.g. H2,...)
        print('delete row', Array[0][3] )



        if Array[0][3] == 'H2':
            print('header deleted')
            del Array[0]
        elif len(Array) > 47:
            del Array[-1] 
        f.close()

        return Array
    except Exception as ex:
        print('***Failed to read in file! *** \n \n' + str(ex))


def deleteCol(Array, Material = False):
    """
    Deletes the extra columns of a loaded file written in the VASCO old format
    Parameters:
    ----------
    :param Array: (numpy.array): Array containing an input  written in the VASCO old format
    :param Material: (bool) : If True, this function interprets that Array contains information of a material and
    assigns to the output array 9 rows. The extra rows are deleted.

    Returns:
    -------
    :return Array: (np.array)
    """
    print "deleteCol"
    #delete the first threee coloumns of Array and transforms all entries to float numbers
    #Number = number of coloumns that will be deleted, starting from left side
    #delete beginning columns


    #delete first 3 coloumns:
    #for i in range(0, len(Array)):
        #for j in range(0,NBegin):
        #    del Array[i][0] # A[i][0] since when an entry is deleted array is shifted anyway to the left!
    
    '''
    #delete end columns
    for i in range(0, len(Array)):
        index=len(Array[0])-NEnd
        for j in range(0,NEnd):
            print('delete one col')
            del Array[i][index+1]
    '''
    #transform all values to float 

    '''
    for i in range(0, len(Array)):
        if Material == True and i ==9:
            # if material is saved with an empty line at the end, then delete it!
            print 'material had too many lines' 
            del Array[i]
            break
        for j in range(len(Array[0])):
            print i,j, Array[i]
            try:
                Array[i][j]=float(Array[i][j])
            except ValueError:

                print i, j, 'Error in deleteCol(InputTransform.py):  Input-array must consits of pure numbers, not "%s" at position ( %s , %s ) by deleting ? column(s)' #% (Array[i][j],i,j)
                break
            except IndexError:
                print i, j, 'Error in deleteCol(InputTransform.py):  List index is out of range for "%s" at position ( %s , %s ) by deleting ? column(s)' % (Array[i][j],i,j)
                break
                #sys.exit(1)
    print Array
    '''
    for i in range(0, len(Array)):
        if Material == True and i == 9:
            # if material is saved with an empty line at the end, then delete it!
            print 'material had too many lines'
            del Array[i]
            break

        #for d in Array[i]:
        #    print d,d.split("e")[0].isdigit(), d.split(".")[0].isdigit(), d.isdigit(), (d.split("e")[0].isdigit() or d.split(".")[0].isdigit() or d.isdigit())
        Array[i] = [d.strip('\n') for d in Array[i]]
        Array[i] = [float(d) for d in Array[i] if (d.split("e")[0].isdigit() or d.split(".")[0].isdigit() or d.isdigit() or d[1:].split(".")[0].isdigit())]
        print Array[i], len(Array[i])

    return Array

def AddMaterial(Array, Name='M'):
    """

    :param Array:
    :param Name:
    :return:
    """
    print "AddMaterial"
    #array keeps the information about one new material
    caption = [ "alpha", "eta_ion", "", "", "", "eta_e", "eta_ph", "Cbs", "Qth"]
    Temp=[]
    dir = Config.Config.MaterialFolder+'\\' +Name + '.csv' # change to idname and i in name

    f=open(dir,'w+')
    f.write(Name +','+ 'H2' +','+'CH4'+','+'CO'+','+'CO2'+','+'\n')
    i=0
    while i<len(Array):
        f.write(str(caption[i])+','+str(Array[i][0])+','+str(Array[i][1])+','+str(Array[i][2])+','+str(Array[i][3])+'\n')
        i+=1
    f.close()


def CheckMaterial(Array):
    """
    Checks Array if some segments = (4 coloumns) have the same material properties; check only among the current inputfile \n
    - if yes, then delete one segment from Array
      Materiallist has length of number of segments and its values are due to which material the segment has, e.g. MaterialList[2] = 0 means that
      the thierd segment has material 1 properties!
    - if no, then add the new material to ArrayList and specify a new number for the material in MaterialList

    Properties:
    ----------
    :param Array: (np.array): Array containing the properties of a Material expressed in VASCO format. \m

    Returns:
    --------
    :MaterialList: (list)  used for SegmentFIle
    :arrayList: (list)  used to define new materials in materialsfolder.

    """
    print "CheckMaterial"
    #checks Array if some segments = (4 coloumns) have the same material properties; check only among the current inputfile
    #- if yes, then delete one segment from Array
    #  Materiallist has length of number of segments and its values are due to which material the segment has, e.g. MaterialList[2] = 0 means that
    #  the thierd segment has material 1 properties!
    #- if no, then add the new material to ArrayList and specify a new number for the material in MaterialList
    #Return Values: MaterialList is used for SegmentFIle and arrayList is used to define new materials in materialsfolder.

    dim = 4

    N= int(len(Array[0])/dim)
    MaterialList=[0]
    ArrayList=[]
    Temp=np.empty([9,dim])

    for s in range(0,N):
        #alpha
        k=0
        for j in range(0,dim):
            Temp[k][j]=Array[j][s*dim+j] +Array[j+4][s*dim+j]
        #ion
        for i in range(8,12):
            k+=1
            for j in range(0,dim):
                Temp[k][j]=Array[i][s*dim+j] +Array[i+4][s*dim+j]
        #eta_e
        k+=1
        for j in range(0,dim):
            Temp[k][j]=Array[16][s*dim+j] +Array[17][s*dim+j]
        #eta_ph
        k+=1
        for j in range(0,dim):
            Temp[k][j]=Array[18][s*dim+j] +Array[19][s*dim+j]
        #beam screen pumping
        k+=1
        for j in range(0,dim):
            Temp[k][j]=Array[20+j][s*dim+j]
        #material outgassing
        k+=1
        for j in range(0,dim):
            Temp[k][j]=Array[24][s*dim+j]
        #temporary array updated. Now check if already existing:
        print "Temp =", Temp
        if not ArrayList:
            ArrayList.append(copy.copy(Temp))
            continue
        Index=0
        for array in ArrayList:

            TotalBoolean=True
            for i in range(0, len(array)):
                if not all(np.array(array[i]) == np.array(Temp[i])):
                    TotalBoolean=False

                    #print('line', i, 'is not identical in Checkmaterial', array, Temp)
                #helpBoolean=np.allclose(np.array(array[i]), np.array(Temp[i]))
                #if not helpBoolean:
                    #TotalBoolean=False

            #Since outgassing is given in pressure, it is usually very small!
            #if any(np.array(array[len(array)-1]) != np.array(Temp[len(array)-1])):
                #TotalBoolean=False

            if TotalBoolean: #np.allclose(array, Temp):
                MaterialList.append(Index)
                #print('old Material')
                break
            elif Index == len(ArrayList)-1:
                ArrayList.append(copy.copy(Temp))
                MaterialList.append(Index+1)
                TotalBoolean=True
                
                #print('new Material')
                break
            else:
                Index += 1
                #print('next index')
    print('Soll immer die gleiche sein!!', MaterialList)

    return ArrayList, MaterialList


def NewPump(Array):

    print "NewPump"
    caption_Pump=['S_H2 [l/s]','S_CH4 [l/s]','S_CO [l/s]','S_CO2 [l/s]']
    #Config.Pumps=LoadPumps()
    OldName= Config.Config.Pumps.keys()
    index=0
    for p in Config.Config.Pumps:
        if np.allclose(Config.Config.Pumps[p].Speed, Array):
            return p
        elif index==len(Config.Config.Pumps)-1:
            name = Find_Name(OldName, 'P')
            dir_Pumps= Config.Config.PumpFolder+ name + '.csv'
            f=open(dir_Pumps,'w+')
            f.write(name +','+ '\n')
            for i in range(4):
                f.write(caption_Pump[i] + ',' + str(Array[i]*1.e3) + '\n')
            f.close()
            return name
        else: index += 1


def NewGassource(Array):

    print "NewGassource"
    #checks if array is gassource folder, otherwise it adds it
    caption_Gassource=['g_H2 [l/s]','g_CH4 [l/s]','g_CO [l/s]','g_CO2 [l/s]']
    #Config.Config.Gassources=LoadGassource()
    OldName=Config.Config.Gassources.keys()
    index=0
    for g in Config.Config.Gassources:
        if np.allclose(Config.Config.Gassources[g].GasRelease, Array):
            #print('Gassource already exists', g)
            return g
        elif index==len(Config.Config.Gassources)-1:
            name = Find_Name(OldName, 'G')
            dir_Gassource= Config.Config.GassourceFolder+ name + '.csv'
            f=open(dir_Gassource,'w+')
            f.write(name +','+ '\n')
            for i in range(4):
                f.write(caption_Gassource[i] + ',' + str(Array[i]*1.0*10*Config.Config.kB*Config.Config.RoomTemperature) + '\n')
            f.close()
            #print('Gassource new', name)
            return name
        else: index+=1


def Compare(ArrayList,MaterialList): 
    print "Compare"
    #ArrayList contains list of data arrays with differnt materials from the transformin data file
    #Materiallist contains shortcuts for material for each segment
    #
    # Aim of this function is compare the differnet materials from the uploaded file to alreay exisiting materials in the materials folder

    FileList = [f for f in listdir(Config.Config.MaterialFolder) if isfile(join(Config.Config.MaterialFolder, f))]
    ArrayList1=[] #existing materials
    Name=[] #name of the existing materials
    #load materials from Materialsfolder to ArrayList1 
    for File in FileList:
        print "File", File
        dir = Config.Config.MaterialFolder+File
        LArray=[]
        with open(dir) as f:			
            for line in f.readlines():
                lsplit=line.split(',')
                LArray.append(lsplit)
        Name.append(LArray[0][0])
        del LArray[0]
        LArray=deleteCol(LArray,NBegin=1,NEnd=0,Material=True)
        ArrayList1.append(copy.copy(LArray))
    isCloseOneLine=True
    isCloseAllLines=True
    Index1=0 #index of material from the uploaded file
    for Temp in ArrayList:
        #if Index1 != 0: break
        #print("Index1", Index1)
        Index=0 #index of existing material in materialfolder
        for array in ArrayList1:
            #print('New Material comparing')
            isCloseAllLines=True
            for i in range(len(array)-1):
                isCloseOneLine = np.allclose(np.array(array[i]) , np.array(Temp[i]))
               
                    #print Index, Name[Index], np.array(array[i]), np.array(Temp[i])
                if not isCloseOneLine:
                    #print("NEW MATERIAL BECAUSE LINE WASn not matching", i, Index1, np.array(array[i]), np.array(Temp[i]))
                    isCloseAllLines=False
                    break
            if not all(np.array(array[-1]) == np.array(Temp[-1])):
                #print(np.array(array[-1]) - np.array(Temp[-1]))
                isCloseAllLines=False
                
            if isCloseAllLines: 
                #print("allClose++++++")
                for k in range(Index1, len(MaterialList)):
                    if MaterialList[k] == Index1: #MaterialList[k]:
                        MaterialList[k] = Name[Index]
                #MaterialList[Index1]=Name[Index]
                #print('Matched with Material from Folder')
                Index1+=1
                print ("Material matched with folder!", Name[Index], Index1)
                break
            elif Index == len(ArrayList1)-1:
                isCloseAllLines=True
                print('+++++++++++++new Material', Index1, len(ArrayList1), Index)
                Index1+=1
                break
            else:
                Index += 1
                isCloseAllLines=True
        #Index1+=1
    return MaterialList, Name 



def Main_Material_Transformation(oldInputFile):
    print "Main_Material_Transformation"
    #dir=Config.Config.DataFolder+'Input/MultiGas1.csv'
    dir=oldInputFile
    Array = FileToArray(dir)

    Array = deleteCol(Array)
    DataAllMaterials = copy.copy(Array[14:39][:])
    DataList, MaterialList = CheckMaterial(DataAllMaterials)
    print DataList, MaterialList

    ##########
    # Material
    #DataAllMaterials=copy.copy(Array[14:39][:])
    #DataList, MaterialList = CheckMaterial(DataAllMaterials)
    MaterialList, Name =Compare(DataList, MaterialList)
    print("MaterialList", MaterialList,"Name", Name)
    Config.Config.setCrossSection([float(Array[10][0]), float(Array[11][1]), float(Array[12][2]), float(Array[13][3]) ])
    j=0
    for i in range(len(MaterialList)):
        if isinstance(MaterialList[i], int):
            name=Find_Name(Name, 'M')
            Name.append(name)
            AddMaterial(DataList[MaterialList[i]], name) #adds material as a csv file in materials folder
            Config.Config.AddMaterial(name + '.csv') #adds material in the program to the materialvariable!

            for k in range(i+1,len(MaterialList)):
                if MaterialList[k]==MaterialList[i]:
                    MaterialList[k]=name
            MaterialList[i]=name
            j+=1

    NOfSegments = len(MaterialList)
    if not int(NOfSegments) == int(len(Array[0])/4):
        print('Warning: Number of Segments is not matching')

    #Config.Config.Pumps
    PumpList=[]

    for j in range(NOfSegments):
        Temp= np.array([float(Array[5][j*4]), float(Array[6][1+j*4]), float(Array[7][2+j*4]), float(Array[8][3+j*4])])*1.e-3
        Pump_Name = NewPump(Temp)
        PumpList.append(Pump_Name)

    Temp= np.array([float(Array[42][0]), float(Array[43][1]), float(Array[44][2]), float(Array[45][3])])*1.e-3
    Pump_Name = NewPump(Temp)
    PumpList.append(Pump_Name)

    #Gassources
    GassourcesList=[]

    for j in range(NOfSegments):
        Temp= np.array([float(Array[9][j*4]), float(Array[9][1+j*4]), float(Array[9][2+j*4]), float(Array[9][3+j*4])])*1.0*0.1/Config.Config.kB/Config.Config.RoomTemperature
        Gassources_Name = NewGassource(Temp)
        GassourcesList.append(Gassources_Name)

    Temp= np.array([float(Array[46][0]), float(Array[46][1]), float(Array[46][2]), float(Array[46][3])])*1.0*0.1/Config.Config.kB/Config.Config.RoomTemperature
    Gassources_Name = NewGassource(Temp)
    GassourcesList.append(Gassources_Name)

    ########
    # Segment

    parts=oldInputFile.split('/')
    Name_Simulation= parts[-1][:-4]
    caption_Seg = [ "d[mm]", "L[mm]", "T[K]", "Material", "Pump", "Gassource", "Photon flux", "Electron flux"]
    #dir_Seg =  oldInputFile[:-4] + '_New.csv'
    dir_Seg = Config.Config.DataFolder + 'Input/' + Name_Simulation + '_New.csv'
    Config.Config.DataFile = dir_Seg
    try:
        f=open(dir_Seg,'w+')
    except IOError:
        print 'Could not open file! It exists already. Please close it and it will be overwritten then! '
        return False

    #f=open(dir_Seg,'w+')

    f.write(Name_Simulation)
    for j in range(NOfSegments):
        f.write(','+'S'+str(j+1))
    f.write('\n')


    f.write(str(caption_Seg[0])) #Diameter
    for j in range(NOfSegments):
        f.write(','+str(Array[1][j*4]))
    f.write('\n')

    f.write(str(caption_Seg[1])) #Length
    for j in range(NOfSegments):
        f.write(','+str(Array[2][j*4]))
    f.write('\n')

    f.write(str(caption_Seg[2])) #VapPressure
    for j in range(NOfSegments):
        f.write(','+str(Array[4][j*4]))
    f.write('\n')

    f.write(str(caption_Seg[3])) #Material
    for j in range(NOfSegments):
        f.write(','+str(MaterialList[j]))
    f.write('\n')

    f.write(str(caption_Seg[4])) #Pumps
    for j in range(NOfSegments+1):
        f.write(','+str(PumpList[j]))
    f.write('\n')

    f.write(str(caption_Seg[5])) #Gassource
    for j in range(NOfSegments+1):
        f.write(','+str(GassourcesList[j]))
    f.write('\n')

    f.write(str(caption_Seg[6])) #PhotonFlux
    for j in range(NOfSegments):
        f.write(','+str(Array[41][j*4]))
    f.write('\n')

    f.write(str(caption_Seg[7])) #Electronflux
    for j in range(NOfSegments):
        f.write(','+str(Array[40][j*4]))
    f.write('\n')

    f.close()
    return True


def Find_Name(OldName, type, initialNumber=1):
    print "Find_Name"
    if type == 'M':
        name='M'+str(initialNumber)
    elif type=='G':
        name='G'+str(initialNumber)
    elif type=='P':
        name='P'+str(initialNumber)
    else: print('type is not recognized')

    if name in OldName:
        initialNumber += 1
        name = Find_Name(OldName, type, initialNumber)
    return name


#made for inputfile old withut headlines


