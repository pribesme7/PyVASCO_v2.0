
def UploadData_3(dir):

    #with open(dir,'r') as csvfile:
	    #spamreader = csv.reader(csvfile, delimiter=' ?, quotechar =')

    f = open(dir, 'r') 	
    Array=[]
    
    i=0
    for line in f: # f.readlines():
        Array.append(line.split(','))    
    f.close()

    
    #Array = np.loadtxt(dir,float)

    X=[]
    Y1=[]
    NRows=len(Array)
    for row in range(NRows): 
        x = float(Array[row][0])
        y = float(Array[row][1])

        X.append(x)
        Y1.append(y)

    return X, Y1



x, y = UploadData('C:/Test/UploadDataTest1.csv')
"""
for index, (u,v) in enumerate(zip(x,y)):
    x[index] = float(u)
    y[index] = float(v)
"""    
     
