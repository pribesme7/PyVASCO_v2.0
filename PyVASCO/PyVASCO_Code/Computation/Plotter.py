from pyqtgraph.Qt import QtGui, QtCore
from PyQt4.QtCore import QPointF
from PyQt4.QtGui import QPolygonF,QColor,QGraphicsTextItem
import pyqtgraph as pg
import numpy as np
from numpy.lib.scimath import sqrt as csqrt
from math import sqrt
import time
from operator import itemgetter
import datetime
from scipy.linalg import expm

from Config import Config


import Computation 


def GetSolutions(Ms,bs,Ls,Ps,SegTemp,Num=Config.NumPointsVacProfile ,Xinit=0, As = np.array([ 1.57603615,  0.55867918,  0.42280604,  0.33730696])):
    """
    Computes the dynamic pressure profile considering a Multi-Gas model with 4 main gas species (H2, CH4, CO, CO2).
    See Refs. [1,2] in docs/.

        @param Ms: (ndarray) : Matrix for equation y' = My + b
        @param bs: (ndarray) : Vector for equation y' = My + b
        @param Ls: (ndarray) : Length of the segment  [m]
        @param Ps: (list) : Integration constants which satisfy the imposed boundary conditions.
        @param Num: (int) : Number of points to in the solution
        @param Xinit: (int) : Initial position of the studied sector of the accelerator, with respect to  IP1 (ATLAS)

        @return Solutions: (list) : Dynamic density profile of the studied sector of the accelerator. Each element of the
        list Solutions is a list [s , n], where
            * @return s: (float) : position along the beampipe [m]
            * @return n: (float) : Density at position s [m**-3]
    """

    TotalLength=0
    Ls2=[]
    for L in Ls:
        TotalLength+=L
        Ls2.append(TotalLength)
    Step=1.0*TotalLength/Num
    xp = np.arange(0,TotalLength,Step)
    i=0
    Len=0
    X=[]
    Solutions=[]
    TempProfile = []
    #for x in xp:
    #    if x > Ls2[i]:   
    #        i+=1
    #    a = As[i]

    #    if np.ndim(Ms[i]) == 2: #Multigas
    #        Solution=np.dot(expm(Ms[i]*(x-Len)),Ps[i])-np.linalg.solve(Ms[i],bs[i]) 
    #    else:
            
    #        p=np.array(Ps[i]).flatten()
    #        c1 = p[0:4]
    #        c2 = p[4:8]


    #        if (Ms[i] == np.zeros(4)).all():
    #            print 'case: B = zeromatrix'
    #            Solution = c1  + c2 * x  + x**2 * bs[i]/(2*a)
    #        else:
    #            Solution = c1 * np.exp(np.sqrt(-Ms[i]/a)*x) + c2 * np.exp(-np.sqrt(-Ms[i]/a)*x) - bs[i]/Ms[i]
    #            Solution = np.reshape(Solution,(4,1))
    #    Solutions.append([x,Solution])
    x=0       
    seg = 0 
    while i<len(Ms):    
        X.append(x+Xinit)  
        if np.ndim(Ms[i]) == 2: #Multigas
            Solution = np.dot(expm(Ms[i]*(x-Len)),Ps[i]) - np.linalg.solve(Ms[i],bs[i]) 
            print ("fundamental:",np.dot(expm(Ms[i]*(x-Len)),Ps[i]-np.linalg.solve(Ms[i],bs[i])))
            print ("particular:",np.dot(expm(Ms[i]*(x-Len))- np.identity(8), np.linalg.solve(Ms[i],bs[i])))
            print ("parameters:", Ps[i]-np.linalg.solve(Ms[i],bs[i]))
            print i, seg, np.linalg.eigh(Ms[i])
            Ps_stability_pos = Ps[i] + 0.001*Ps[i]
            Ps_stability_neg = Ps[i] - 0.001*Ps[i]
            sol_up = np.dot(expm(Ms[i]*(x-Len)),Ps_stability_pos)-np.linalg.solve(Ms[i],bs[i])
            sol_down = np.dot(expm(Ms[i]*(x-Len)),Ps_stability_neg)-np.linalg.solve(Ms[i],bs[i])
            print('upper limit', sol_up-Solution,'lower limit', sol_down-Solution,'delta limit', (sol_up-sol_down)/Solution)
            delta = (sol_up-sol_down)/Solution
            #if np.max(delta) > 10:
                #print seg, delta
        else:
            a = As[i]
            p=np.array(Ps[i]).flatten()
            c1 = p[0:4]
            c2 = p[4:8]


            if (Ms[i] == np.zeros(4)).all():
                Solution = c1  + c2 * x  - x**2 * bs[i]/(2*a)
                Solution = np.reshape(Solution,(4,1))
            else: #Single gas framework
                Solution = np.array([0.,0.,0.,0.])
                val = Ms[i]/a
                val2 = bs[i]/Ms[i] # particular solution
                for j, v in enumerate(val):
                    if v > 0: # ion desorption term is higher than sticking probability (B has positive entries in diagonal!)
                        Solution[j] = c1[j] * np.cos(np.sqrt(v)*x) + c2[j] * np.sin(np.sqrt(v)*x) - val2[j]
                    else: 
                        Solution[j] = c1[j] * np.exp(np.sqrt(-v)*x) + c2[j] * np.exp(-np.sqrt(-v)*x) - val2[j]

                #Solution = c1 * np.cos(np.sqrt(Ms[i]/a)*x) + c2 * np.sin(-np.sqrt(Ms[i]/a)*x) - bs[i]/Ms[i]
                #Solution = c1 * np.exp(np.sqrt(-Ms[i]/a)*x) + c2 * np.exp(-np.sqrt(-Ms[i]/a)*x) - bs[i]/Ms[i]
                Solution = np.reshape(Solution,(4,1))


        Solutions.append([x+Xinit,Solution])
        TempProfile.append([x+Xinit,SegTemp[i]])
        x+=Step
        while i<len(Ms) and x-Len>Ls[i]:        
            Len+=Ls[i]
            i+=1
            seg+=1

    #print "In GetSolutions =", TempProfile
    return Solutions,TempProfile

def PlotSegments():
    """
    Generates a list of QPolygonF objects which can be plotted using PyQt plotting library. \n

        @return Poligons: (list) : Each element of the list has the form [QPolygonF(Vertices), Color, 1, Name], where\n
            * @return QPolygonF: (QPolygonF) : Polygon built from the vertices of a segment \n
            * @return Color: (list) : RGB color of the segment. It is computed according to the properties of temperature,
                                    average Outgassing and the average effective pumping speed. \n
            * @return Name: (string) : Name of the segment. \n
    """

    Segments, EndPump, EndSource, GeometryParameters= GetSegments()
    if Segments == False:
        #QMessageBox.warning(self, "ERROR in Input Parameters", "Please define the Input parameter correctly! Could not find item: ", EndPump , QMessageBox.Ok)
        return 
    Maxs=[0,0,0]

    Polygons=[[],[]]

    for Beam in range(0,2):

        

        for OneSegment in Segments[Beam]:
            S=OneSegment.S
            R=np.sqrt(0.5*(OneSegment.Area[0]+OneSegment.Area[1])/np.pi)
            Temperature=OneSegment.GetTemperature()
            VelocityMean=np.sqrt(8*Config.kB*Temperature/math.pi/Config.Mass)

            Blue=Temperature
            Green=np.average(0.5*(OneSegment.Perimeter[0]+OneSegment.Perimeter[1])*(OneSegment.Material.OutGassing/OneSegment.Temperature))
            Red=np.average(0.5*(OneSegment.Perimeter[0]+OneSegment.Perimeter[1])/4*VelocityMean*(OneSegment.Material.Sticking)+OneSegment.Material.LinearPumping)

            Color=[Red,Green,Blue]

            for i in range(0,3):
                if Color[i]>Maxs[i]:
                    Maxs[i]=Color[i]

            Vertices=[]
            W=0.3
            Vertices.append( QPointF(S[0]/Config.ScalingXAxis,((-R+(Beam-0.5)*W)/Config.ScalingXAxis)*Config.ZoomPlot))
            Vertices.append( QPointF(S[0]/Config.ScalingXAxis,((R+(Beam-0.5)*W)/Config.ScalingXAxis)*Config.ZoomPlot))
            Vertices.append( QPointF(S[1]/Config.ScalingXAxis,((R+(Beam-0.5)*W)/Config.ScalingXAxis)*Config.ZoomPlot))
            Vertices.append( QPointF(S[1]/Config.ScalingXAxis,((-R+(Beam-0.5)*W)/Config.ScalingXAxis)*Config.ZoomPlot))

            Polygons[Beam].append([QPolygonF(Vertices),Color,1,OneSegment.Name])

           
    for Beam in range(0,2):
        PI=0
        while PI<len(Polygons[Beam]):   
            Polygons[Beam][PI][1]=QColor(int(Polygons[Beam][PI][1][0]/Maxs[0]*255),int(Polygons[Beam][PI][1][1]/Maxs[1]*255),int((1-Polygons[Beam][PI][1][2]/Maxs[2])*255))
            PI+=1


    return Polygons


