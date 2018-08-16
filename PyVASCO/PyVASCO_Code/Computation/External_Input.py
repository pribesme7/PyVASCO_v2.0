from __future__ import division
import numpy as np

def External_Ph_Flux(LengthSegments, Array):
    ''' LengthSegments: is an array,
            its entries represent the length of each segment
        Array: is a 2-dimensional array, the first coordinate 
            is the x-value and the second is the photon flux at this point
     '''
    i = 1  # indicating Length of
    x_coord, Photonflux = Array
    sum_x = 0
    Gamma = []
    index_old = 0
    totalLength = LengthSegments[0]
    Ph_Flux_Per_Segment_List=[]
    lenX = len(LengthSegments)
    for index, x in enumerate(x_coord):
        while x > totalLength:
            print 'x', x
            if index == index_old:
                Ph_Flux_Per_Segment = Photonflux[index - 1]

            else: 
                Ph_Flux_Per_Segment = np.sum(Photonflux[index_old:index]) / (index-index_old)
            Ph_Flux_Per_Segment_List.append(Ph_Flux_Per_Segment)
            try: totalLength += LengthSegments[i]       
            except IndexError:
                print('Your geometry is shorter than your x-coordinates \
                of the photon flux! The rest of the values are not \
                read in anymore! Please be sure, that everything is correct')
                break      
            index_old = index
            i += 1

    Ph_Flux_Per_Segment = np.sum(Photonflux[index_old:index + 1]) / (index + 1 - index_old)
    Ph_Flux_Per_Segment_List.append(Ph_Flux_Per_Segment)
    
    return Ph_Flux_Per_Segment_List



