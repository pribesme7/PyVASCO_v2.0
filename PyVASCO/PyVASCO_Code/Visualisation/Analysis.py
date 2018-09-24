#from Config import Config.kB as kB
kB = 1.3806488e-23


def _UploadData(dir):

    try:
        f=open(dir,'r')
        Array=[]
    
        i=0
        for line in f: # f.readlines():
            Array.append(line.split(','))    
        f.close()
        del Array[0]
    except Exception as ex:
        print('***Failed to read in file! *** \n \n'+ dir + str(ex))
        return []

    NRows = len(Array)
    NCols = len(Array[0])
    data = [[] for _ in xrange(NCols)]
    for row in range(NRows): 
        for col in range(NCols):
            try:
                data[col].append(float(Array[row][col]))
            except Exception as ex:
                print('***Failed to read out the array! Wrong input format? *** \n \n'+ dir + str(ex))
                return []
    return data




def runAnalysis(inst, dir1, dir2):
    """
    Loads data from different sources (directories) and plots it together in the Tab 'Analysis and Comparison' of the 'Analysis' tab in PyVASCO. 
    @param  inst: Density profile
    @param  dir1: Directory where there is stored data to upload and compare with inst
    @param  dir2: Directory where there is stored data to upload and compare with inst
    @return:  True
    """
    labelStyle = {'color': '#FFF', 'font-size': '14pt' , 'height': '10pt'}
    inst.AnalysisPlotWidget.setLabel('left', "Pressure (mbar)", **labelStyle)
    Plots = [ inst.Plot1, inst.Plot2, inst.Plot3, inst.Plot4, inst.Plot5, inst.Plot6, inst.Plot7, inst.Plot8]
    PlotsCheckBox = [ inst.Plot1CheckBox, inst.Plot2CheckBox, inst.Plot3CheckBox, inst.Plot4CheckBox, inst.Plot5CheckBox, inst.Plot6CheckBox, inst.Plot7CheckBox, inst.Plot8CheckBox]
    factor = [1.0, 300*kB*1.e-2, 1.0, 1.e2/300/kB, 0.750062] #conversion factors to transform e.g. pressure to density
    inst.logAnalysis()

    data = _UploadData(dir1) 
    data2 = _UploadData(dir2)

    x_idx = 0
    y_idx = 0
    loop = len(data)
    help = inst.unitComboBox.currentIndex()
    if help in [0,3]:
        inst.AnalysisPlotWidget.setLabel('left', "Density (particles/m2)", **labelStyle)
    if inst.formatComboBox.currentIndex() != 0:
        loop = len(data)/2+1

    calculate_total = False
    if inst.Plot1_All_CheckBox.isChecked():
        calculate_total = True
        total = [x*0 for x in data[0]] # array of zeros with approptiate length

    for i in range(1, loop):
        if inst.formatComboBox.currentIndex() == 0:
            x_idx=0
            y_idx=i
        else: 
            x_idx= (i-1)*2
            y_idx = x_idx+1
        if PlotsCheckBox[i-1].isChecked():
            try: 
                data[y_idx]=[x*factor[help] for x in data[y_idx]]
                Plots[i-1].setData(x=data[x_idx], y= data[y_idx])
            except Exception as ex:
                return False

            #calculate total density of plot 1-4:
            if calculate_total:
                total = map(lambda x,y:x+y, total,data[y_idx])
                Plots[i-1].clear() #plot only total
        else:
            Plots[i-1].clear()
    
    if calculate_total:
        calculate_total = False
        inst.Plot1_total.setData(x=data[x_idx], y= total)
    else: inst.Plot1_total.clear()
      



    loop = len(data2)

    help = inst.unit2ComboBox.currentIndex()
    if inst.format2ComboBox.currentIndex() != 0:
        loop = len(data2)/2+1

    calculate_total2 = False
    if inst.Plot5_All_CheckBox.isChecked():
        calculate_total2 = True
        total2 = [x*0 for x in data2[0]] # array of zeros with approptiate length


    for i in range(1, loop):
        if inst.format2ComboBox.currentIndex() == 0:
            x_idx=0
            y_idx=i
        else: 
            x_idx= (i-1)*2
            y_idx = x_idx+1
        if PlotsCheckBox[4+i-1].isChecked():
            try: 
                data2[y_idx]=[x*factor[help] for x in data2[y_idx]]
                Plots[4+i-1].setData(x=data2[x_idx], y= data2[y_idx])
            except Exception as ex:
                return False
                    #calculate total density of plot 4-8:
            if calculate_total2:
                total2 = map(lambda x,y:x+y, total2,data2[y_idx])
                Plots[4+i-1].clear() #plot only total

        else:
            Plots[4+i-1].clear()

    if calculate_total2:
        calculate_total2 = False
        inst.Plot5_total.setData(x=data2[x_idx], y= total2)
    else: inst.Plot5_total.clear()

    return True