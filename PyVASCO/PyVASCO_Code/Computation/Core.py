from __future__ import division

from sympy import *
import numpy as np
from numpy.linalg import inv
from numpy.lib.scimath import sqrt as csqrt
#from scipy.linalg import expm2 as expm
from scipy.linalg import expm
import scipy.linalg
#from Timer import Timer
import Config
# import bigfloat ( package that supports large numbers; mathematic operations are sometimes not working correctly with these numbers!  )

def PrintMatrix(A):
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


#Solve returns the parameters that classifies the solution
def Solve(Ms,  bs,  Ls,  Ss,  gs,  As): #single gas and multi gas combined
    """
    Solves the linear system presented in the user guide to obtain the list of integration constants which satisfy the imposed boundary conditions.  A Multi-Gas model in which the dominant species (H2,CH4,CO and CO2) can interact is considered. \n

    Parameters:
    -----------
        :param Ms: (ndarray) : Matrix for equation y' = My + b
        :param bs: (ndarray) : Vector for equation y' = My + b
        :param Ls: (float) : Length of the segment  [m]
        :param Ss: (list) : Punctual pumping speeds [m**3/s]
        :param gs: (list) : Punctual gas sources
        :param As: (ndarray) : Specific conductances
    Returns:
    --------
        :param  Ps: (list) :  Integration constants which satisfy the imposed boundary conditions.
    """
    print('Solve')    
    #Ms, bs- Matrices and vectors for equation y' = My + b
    #Ls-lenghts of segment
    #SS- point pumping speeds
    #gs- point gas sources
    Is_Single_Gas = []
    for i in range(len(Ms)):
        if Ms[i].shape[0] == 8:
            Is_Single_Gas.append(False)
        else: Is_Single_Gas.append(True)
    #for pumping condition we need to add the last segment again
    if Ms[-1].shape[0] == 8: Is_Single_Gas.append(False)
    else:
        Is_Single_Gas.append(True)

    # Preparing the inputs - adding two virtual segments at the beginning and the end:
    N = len(Ms)
    Dim = 8 
    Dim_half = 4
    xinit = 0
    Ms2 = Ms
    bs2 = bs
    As2 = As
    Ls2 = []
    Ls_Singlegas = []
    total = 0
    for L in Ls:
        total+= L
        Ls2.append(np.sqrt(L))     
        Ls_Singlegas.append(total) 
    Ss2 = []
    gs2 = []
    Hs2 = []
    i = 0

    ########creating Pumping/gassource array
    while i < N + 1:
        if i == 0 or i == N: #mirror condition: half od
            if Is_Single_Gas[i]:
                Ss2.append(Ss[i])
                gs2.append(gs[i])
            else:
                Ss2.append(np.bmat([[np.zeros((Dim_half,  Dim_half)),  np.zeros((Dim_half,  Dim_half))],  [np.diag(Ss[i]) * 0.5,  np.zeros((Dim_half,  Dim_half))]]))        
                gs2.append(np.bmat([[np.zeros((Dim_half,  1))],  [(np.array(gs[i]) * 0.5).reshape(4,  1)]]))            
        else:
            if Is_Single_Gas[i]:
                Ss2.append(Ss[i])
                gs2.append(gs[i])
            else:
                Ss2.append(np.bmat([[np.zeros((Dim_half,  Dim_half)),  np.zeros((Dim_half,  Dim_half))],  [np.diag(Ss[i]),  np.zeros((Dim_half,  Dim_half))]]))
                gs2.append(np.bmat([[np.zeros((Dim_half,  1))],  [(gs[i]).reshape(4,  1)]]))      
        i += 1
    ################

    i = 0
    while i<N:
        if Is_Single_Gas[i]:
            coeff = [As[i], Ms[i], bs[i]]
            Hs2.append(coeff)
        else:
            Hs2.append(np.bmat([[np.identity(Dim_half),  np.zeros((Dim_half,  Dim_half))],  [np.zeros((Dim_half,  Dim_half)),  -np.diag(As2[i])]]))
        i += 1




    #the basis in which the parameters of fundamental solution are calculated:d
   # T = np.bmat([[np.identity(Dim_half), -np.identity(Dim_half)], [np.identity(Dim_half), np.identity(Dim_half)]])
   # TInv = 0.5 * np.bmat([[np.identity(Dim_half), np.identity(Dim_half)], [-np.identity(Dim_half), np.identity(Dim_half)]])        
    T = np.identity(Dim)
    TInv = np.identity(Dim)





    # auxiliary matrices
    Q = np.bmat([[np.zeros((Dim_half, Dim_half)), np.identity(Dim_half)]])
    Zero = np.bmat([[np.zeros((Dim_half, Dim))]])
    Top=[]
    if Is_Single_Gas[0]:
        Top = (np.bmat( [[(alpha(Hs2[0], xinit) * Ss2[0]*0.5 - As[0]*alpha_prime(Hs2[0], xinit))* np.identity(4), (beta(Hs2[0], xinit) * Ss2[0] * 0.5 - As[0] * beta_prime(Hs2[0], xinit))* np.identity(4)]])).reshape((4,8))
    else:
        Top = np.dot(np.bmat([[-np.diag(Ss[0])/2, np.diag(As[0])]]), T)
    #Top = np.dot(np.bmat([[np.identity(Dim_half), np.zeros((Dim_half, Dim_half))]]), T)

    #Creating the solving array
    Top_rhs= []
    if Is_Single_Gas[0]:
        Top_rhs = (-Ss2[0]*0.5*gamma(Hs2[0], xinit) + gs2[0]*0.5 + As[0]*gamma_prime(Hs2[0], xinit)).reshape((4,1))
    else:
        Top_rhs = np.dot(Q, -gs2[0])
    #Top_rhs =  np.array([1/(300 * 1.3806488e-23 * 0.01) * 4.31E-07,  0,  0,  0]).reshape(4, 1)
    SolvingArray = np.bmat([[Top, Zero, Top_rhs]])    
    
    print 'left boundary condition succesfully implemented in SolvingArray'

    i = 0
    while i < N-1:   
        rhs1 = np.zeros(4)
        rhs2 = np.zeros(4)    
        if Is_Single_Gas[i]:
            block1 = np.bmat([[alpha(Hs2[i], Ls_Singlegas[i])* np.identity(4), beta(Hs2[i], Ls_Singlegas[i])* np.identity(4)],
                              [(-As[i]*alpha_prime(Hs2[i], Ls_Singlegas[i]))* np.identity(4), (-As[i]*beta_prime(Hs2[i], Ls_Singlegas[i]))* np.identity(4)]])
            rhs1 = -gamma(Hs2[i], Ls[i]) 
            rhs2 = As[i]*gamma_prime(Hs2[i], Ls[i])
        else:
            MSqrt = scipy.linalg.sqrtm(Ms2[i][Dim_half:Dim, 0:Dim_half]) * Ls2[i] 
            if np.isnan(MSqrt).any():
                print('SQRT of M is NaN for segment: ', i)
                return []
            S = np.bmat([[MSqrt/2, Ls2[i] * np.identity(Dim_half)/2], [-MSqrt/2, Ls2[i] * np.identity(Dim_half)/2]])
            ExpD = np.bmat([[expm(MSqrt * Ls2[i]), np.zeros((Dim_half, Dim_half))], [np.zeros((Dim_half, Dim_half)), expm(-MSqrt * Ls2[i])]])
            ExpT = np.linalg.solve(S, np.dot(ExpD, np.dot(S, T)))
            #print i, Ms2[i]
            try: Mb = np.linalg.solve(Ms2[i], bs2[i])
            except np.linalg.linalg.LinAlgError as err:
                print err 
                return []
            ExpMb = np.dot(ExpT, np.dot(TInv, Mb))
            block1 = np.dot(Hs2[i], ExpT)
            Right = np.dot(Hs2[i], -ExpMb + Mb)
            rhs1 = Right[0:4]
            rhs2 = Right[4:8]


        if Is_Single_Gas[i+1]:
            block2 = np.bmat([[-alpha(Hs2[i+1], Ls_Singlegas[i])* np.identity(4), -beta(Hs2[i+1], Ls_Singlegas[i])* np.identity(4)],
                              [(As[i+1]*alpha_prime(Hs2[i+1], Ls_Singlegas[i]) - Ss2[i+1]*alpha(Hs2[i+1], Ls_Singlegas[i]))* np.identity(4), 
                               (As[i+1]*beta_prime(Hs2[i+1], Ls_Singlegas[i]) - Ss2[i+1]*beta(Hs2[i+1], Ls_Singlegas[i]))* np.identity(4) ]])
            rhs1 +=  gamma(Hs2[i+1], Ls[i])
            rhs2 += - As[i+1]* gamma_prime(Hs2[i+1], Ls[i]) + Ss2[i+1] * gamma(Hs2[i+1], Ls[i]) - gs2[i+1]
            
        else:
            block2 = -np.dot(Ss2[i + 1] + Hs2[i + 1], T)
            #rhs2 -=  np.zeros(4).reshape(4,  1) #gs2[i+1][4:8]
            
        
        rhs = np.bmat([[rhs1], [rhs2]]).reshape(8,1) #vector of (8x1)
        #print("i: ", "block1: ", block1 , "block2: ",block2,  "rhs: ", rhs )
        SolvingArray = np.append(SolvingArray, np.bmat([[block1, block2, rhs]]), axis = 0)
        i += 1
    
    Bottom = []
    Bottom_rhs = []
    i = N-1
    if Is_Single_Gas[i]:
        Bottom = np.bmat( [[(alpha(Hs2[-1], Ls_Singlegas[-1])*Ss2[-1]*0.5 + As[-1]*alpha_prime(Hs2[-1], Ls_Singlegas[-1]))*np.identity(4), (beta(Hs2[-1], Ls_Singlegas[-1])*Ss2[-1]*0.5 + As[-1]*beta_prime(Hs2[-1], Ls_Singlegas[-1]))*np.identity(4)]])
        Bottom_rhs = (-Ss2[-1]*0.5*gamma(Hs2[-1], Ls_Singlegas[-1]) + gs2[-1]*0.5 - As[-1]*gamma_prime(Hs2[-1], Ls_Singlegas[-1])).reshape((4,1))

    else:

        MSqrt = scipy.linalg.sqrtm(Ms2[i][Dim_half:Dim, 0:Dim_half]) * Ls2[i] 
        S = np.bmat([[MSqrt/2, Ls2[i] * np.identity(Dim_half)/2], [-MSqrt/2, Ls2[i] * np.identity(Dim_half)/2]])
        ExpD = np.bmat([[expm(MSqrt * Ls2[i]), np.zeros((Dim_half, Dim_half))], [np.zeros((Dim_half, Dim_half)), expm(-MSqrt * Ls2[i])]])            
        ExpT = np.linalg.solve(S, np.dot(ExpD, np.dot(S, T)))       
        ExpMb = np.dot(ExpT, np.dot(TInv, np.linalg.solve(Ms2[i], bs2[i])))
        Right = np.dot(Hs2[i], -ExpMb + np.linalg.solve(Ms2[i], bs2[i])) - gs2[i + 1]
        #Right = np.dot(Hs2[i], -ExpMb + np.linalg.solve(Ms2[i], bs2[i]))-gs2[i + 1]

        Bottom = np.dot(np.bmat([[-np.diag(Ss[N])/2, -np.diag(As[N-1])]]), ExpT)
        Bottom_rhs = np.dot(Q, Right)


    SolvingArray = np.append(SolvingArray, np.bmat([[Zero, Bottom, Bottom_rhs]]), axis = 0)
    SolvingArray = SolvingArray.astype(float)


    #Solving the results:
    i = 0
    while i<N-2:
        start = i * Dim        
        end = i * Dim + 3 * Dim_half              
        MakeTriangular(SolvingArray, start, end)        
        Exchange(SolvingArray, start + Dim, end)       
        i += 1
   
    MakeTriangular(SolvingArray, (N-2) * Dim, (N) * Dim)    
    MakeDiagFromT(SolvingArray, (N-2) * Dim, (N) * Dim)
    i = N-3

    while i >= 0:
        start = i * Dim
        end = i * Dim + 2 * Dim        
        Exchange(SolvingArray, start + Dim, end)        
        MakeDiagFromT(SolvingArray, start, end)        
        i -= 1  
    #Transformation of parameters back to the y, y' basis
    i = 0
    Ps = []
    #calculation of fundamental system P(x)
    while i<N:
        Sol = SolvingArray[i * Dim:(i + 1) * Dim, 2 * Dim]
        if Is_Single_Gas[i]:
            Ps.append(Sol)
        else:
            Ps.append(np.dot(T, Sol) +  np.linalg.solve(Ms2[i], bs2[i]))      
        
        i += 1

    return Ps #return the initial values of each segment,  PARAMETERS


def MakeTriangular(A, i, j):
    """
    Computes the Triangular matrix of the input matrix A. Matrix A can't contain integer numbers (only floats) \n

    Parameters:
    ----------
        :param A: (ndarray) : Input matrix
        :param i: (int) : Number of rows of A
        :param j: (int) : Number of columns of A
    Returns:
    -------
        :param A: (ndarray) : Triangular matrix of A
    """

    #!!Make sure that A contains only float numbers (not int)!!
    k = 0
    while k<j-i:  
        #Pivotisierung 
        A[i + k:j, :] = (A[i + k : j, :])[((np.absolute(A[i + k:j, k]).A1).argsort())[::-1], :]
        #print 'A', A[i + k:j, :]
        if A[i + k, k] == 0:
            k += 1
            continue  
        
        A[i + k, :] = (A[i + k, :]) * (1./A[i + k, k])   


        l = k + 1
        while l<j-i:            
            if A[i + l, k] == 0:                
                break            
            A[i + l, :] -=  A[i + l, k] * A[i + k, :]    
            #print 'c', A[i + l, :]   
            l += 1
        k += 1
        
def MakeDiagFromT(A, i, j):
    """
    Computes the diagonal matrix from the triangular  input matrix, A.
    Parameters:
    ----------
        :param A: (ndarray) : Input matrix
        :param i: (int) : Number of rows of A
        :param j: (int) : Number of columns of A
    Returns:
    -------
        :param A: (ndarray) : Diagonal matrix
    """

    Dim = A.shape[1]-1
    k = Dim-1
    while k>0:
        l = k-1
        while l >= 0:
            A[i + l, :] -= A[i + k, :] * A[i + l, k]
            l -= 1

        k -= 1
        
def Exchange(A, i, j):
    """
    Exchanges the position of the first half of columns of the input matrix with the second half of columns in the selected interval of rows [i:j). The input matrix, A, has to have an even number of columns.

    Parameters:
    ----------
        :param A: (ndarray) :  Input matrix. It has to have an even number of columns. \n
        :param i: (int) : Index of the first row in which columns have to be exchanged. \n
        :param j: (int) : Index of the first row in which columns shouldn't be exchanged. \n

    Returns:
    -------
        :param A: (ndarray) : Modified matrix

    Examples:
    --------
    >>> A = np.array([[1,2,3,4],[6,7,8,9]])
    >>> Exchange(A,0,1) # Columns will be modified only in the first row
    Out[1]:\n
    array([[ 3,  4,  1,  2],
           [ 6,  7,  8,  9]])
    >>> Exchange(A,0,2) # Columns will be exchanged in the first and second row
    Out[2]:\n
    array([[ 1,  2,  3,  4],
          [ 8,  9,  6,  7]])

    """
    #A col-dimension has to be even!
    Dim = int(A.shape[1]-1) # number of colomns -1

    print 'should be only zeros', A[i:j, 0:int(Dim/2)]

    A[i:j, 0:Dim] = np.concatenate((A[i:j, int(Dim/2):Dim], A[i:j, 0:int(Dim/2)]), axis = 1)

#############
#Single gas coefficients


def alpha(coeff,length):
    """
    Generates auxiliary matrix alpha in the single-gas model. See user guide for more details. \n
    Parameters:
    ----------
    :param coeff: (list): \n
    :param length: (numpy.array): x-coordinates where the matrix alpha is evaluated.\n

    Returns:
    -------
    :returns help: (list) : Auxiliary matrix alpha. See user guide for more information.
    """
    #return np.ones(4)
    [a, b, c] = coeff
    if (b == np.zeros(4)).all():
        return (np.ones(4))
    else:
        help = np.array([0.,0.,0.,0.])
        val = -b/a
        for i,v in enumerate(val):
             if v < 0.:
                 print '2222222222222'
                 help[i] = np.cos(np.sqrt(-v)*length)
             else: 
                 print '1111111111111'
                 help[i] = np.exp(np.sqrt(v)*length)
        return help
        #return np.exp(np.sqrt(-b/a)*length)


def beta(coeff,length):
    """
    Generates auxiliary matrix beta in the single-gas model. See user guide for more details. \n
    Parameters:
    ----------
    :param coeff: (list): \n
    :param length: (numpy.array): x-coordinates where the matrix beta is evaluated.\n

    Returns:
    -------
    :returns help: (list) : Auxiliary matrix beta. See user guide for more information.
    """
    #return (np.ones(4)*100)
    [a, b, c] = coeff
    print "b = ", b
    if (b == np.zeros(4)).all():
        return np.ones(4)*length
    else:
        help = np.array([0.,0.,0.,0.])
        val = -b/a
        for i,v in enumerate(val):
             if v < 0.:
                 print '2222222222222'
                 help[i] = np.sin(np.sqrt(-v)*length)
             else: 
                 print '1111111111111'
                 help[i] = np.exp(-np.sqrt(v)*length)
        return help
        #return np.exp(-np.sqrt(-b/a)*length)


def gamma(coeff,length):
    """
    Generates auxiliary matrix gamma in the single-gas model. See user guide for more details. \n
    Parameters:
    ----------
    :param coeff: (list): \n
    :param length: (numpy.array): x-coordinates where the matrix gamma is evaluated.\n

    Returns:
    -------
    :returns help: (list) : Auxiliary matrix gamma. See user guide for more information.
    """
    #return (np.ones(4)*3)
    [a, b, c] = coeff
    if (b == np.zeros(4)).all():
        print "gamma =", -length**2 * c/(2.*a),"*x^2"
        return  -length**2 * c/(2.*a)
    else:
        return -c/b


def alpha_prime(coeff,length):
    """
    Generates auxiliary matrix alpha'  in the single-gas model. See user guide for more details. \n
    Parameters:
    ----------
    :param coeff: (list): \n
    :param length: (numpy.array): x-coordinates where the matrix alpha' is evaluated.\n

    Returns:
    -------
    :returns help: (list) : Auxiliary matrix alpha'. See user guide for more information.
    """
    #return (np.ones(4)*2)
    [a, b, c] = coeff
    if (b == np.zeros(4)).all():
        return np.zeros(4)
    else:
        help = np.array([0.,0.,0.,0.])
        val = -b/a
        for i,v in enumerate(val):
             if v < 0.:
                 print '2222222222222'
                 help[i] = -np.sqrt(-v)*np.sin(np.sqrt(-v)*length)
             else: 
                 print '1111111111111'
                 help[i] = np.sqrt(v)*np.exp(np.sqrt(v)*length)
        return help    

        #return np.sqrt(-b/a)*np.exp(np.sqrt(-b/a)*length)


def beta_prime(coeff,length):
    """
    Generates auxiliary matrix beta' in the single-gas model. See user guide for more details. \n
    Parameters:
    ----------
    :param coeff: (list): \n
    :param length: (numpy.array): x-coordinates where the matrix beta' is evaluated.\n

    Returns:
    -------
    :returns help: (list) : Auxiliary matrix beta'. See user guide for more information.
    """
    #return (np.ones(4)*200)
    [a, b, c] = coeff
    if (b == np.zeros(4)).all():
        return np.ones(4)
    else:
        help = np.array([0.,0.,0.,0.])
        val = -b/a
        for i,v in enumerate(val):
             if v < 0.:
                 print '2222222222222'
                 help[i] = np.sqrt(-v)*np.cos(np.sqrt(-v)*length)
             else: 
                 print '1111111111111'
                 help[i] = -np.sqrt(v)*np.exp(-np.sqrt(v)*length)
        return help    
        #return -np.sqrt(-b/a)*np.exp(-np.sqrt(-b/a)*length)


def gamma_prime(coeff,length):
    """
    Generates auxiliary matrix beta' in the single-gas model. See user guide for more details. \n
    Parameters:
    ----------
    :param coeff: (list): \n
    :param length: (numpy.array): x-coordinates where the matrix beta' is evaluated.\n

    Returns:
    -------
    :returns help: (list) : Auxiliary matrix beta'. See user guide for more information.
    """
    #return (np.ones(4)*3)
    [a, b, c] = coeff
    if (b == np.zeros(4)).all():
        return -length*c/a
    else:
        return np.zeros(4)


#this was used only for testing, now: whole functionality is implemented in "Solve"
'''
def Solve_Singlegas(Bs, Cs, Ls, Ss, Gs, As): #_Singlegas
    #input values are all (4x4) vectors
    #returns the constants C1 and C2 for each segment that define the solution function
    print("Singlegas")
    N = len(As)
    coeff = []
    Ls2 = []
    total = 0
    for L in Ls:
        total+= L
        Ls2.append(total)  
    print Ls2
    i = 0
    while i < N: 
        coeff.append([As[i], Bs[i], Cs[i]])         
        pumping = np.array(Ss[i])
        gassource = np.array(Gs[i])
        i+=1

    
    #creation of solving array:
    xinit = 0
   

    Top = (np.bmat( [[(alpha(coeff[0], xinit) * Ss[0]*0.5 - As[0]*alpha_prime(coeff[0], xinit))* np.identity(4), (beta(coeff[0], xinit) * Ss[0] * 0.5 - As[0] * beta_prime(coeff[0], xinit))* np.identity(4), np.zeros([4,4]), np.zeros([4,4])]])).reshape((4,16))
    
    Top_rhs = (-Ss[0]*0.5*gamma(coeff[0], xinit) + Gs[0]*0.5 + As[0]*gamma_prime(coeff[0], xinit)).reshape((4,1))
    
    SolvingArray = np.bmat([[Top, Top_rhs]])   



    i = 0
    while i < N-1: 
        block1 = np.bmat([[alpha(coeff[i], Ls2[i])* np.identity(4), beta(coeff[i], Ls2[i])* np.identity(4)],
                          [(-As[i]*alpha_prime(coeff[i], Ls2[i]))* np.identity(4), (-As[i]*beta_prime(coeff[i], Ls2[i]))* np.identity(4)]])
        block2 = np.bmat([[-alpha(coeff[i+1], Ls2[i])* np.identity(4), -beta(coeff[i+1], Ls2[i])* np.identity(4)],
                          [(As[i+1]*alpha_prime(coeff[i+1], Ls2[i]) - Ss[i+1]*alpha(coeff[i+1], Ls2[i]))* np.identity(4), 
                           (As[i+1]*beta_prime(coeff[i+1], Ls2[i]) - Ss[i+1]*beta(coeff[i+1], Ls2[i]))* np.identity(4) ]])
        rhs = (np.bmat([
            [-gamma(coeff[i], Ls[i]) + gamma(coeff[i+1], Ls[i])],
            [As[i]*gamma_prime(coeff[i], Ls[i]) - As[i+1]* gamma_prime(coeff[i+1], Ls[i]) +Ss[i+1]*gamma(coeff[i+1], Ls[i]) - Gs[i+1]]])).reshape(8,1)
        
        SolvingArray = np.append(SolvingArray, np.bmat([[block1, block2, rhs]]), axis = 0)
        i+=1

    Bottom = np.bmat( [[np.zeros([4,4]), np.zeros([4,4]), (alpha(coeff[-1], Ls2[-1])*Ss[-1]*0.5 + As[-1]*alpha_prime(coeff[-1], Ls2[-1]))*np.identity(4), (beta(coeff[-1], Ls2[-1])*Ss[-1]*0.5 + As[-1]*beta_prime(coeff[-1], Ls2[-1]))*np.identity(4)]])
    Bottom_rhs = (-Ss[-1]*0.5*gamma(coeff[-1], Ls2[-1]) + Gs[-1]*0.5 - As[-1]*gamma_prime(coeff[-1], Ls2[-1])).reshape((4,1))
    SolvingArray = np.append(SolvingArray, np.bmat([[Bottom, Bottom_rhs]]), axis = 0)
    SolvingArray = SolvingArray.astype(float)



    Dim = 8
    #Solving the results:
    i = 0
    while i<N-2:
        start = i * Dim        
        end = i * Dim + 3 * Dim/2              
        MakeTriangular(SolvingArray, start, end)      
        Exchange(SolvingArray, start + Dim, end) 
        i += 1
   
    MakeTriangular(SolvingArray, (N-2) * Dim, (N) * Dim)    
    #print SolvingArray
    MakeDiagFromT(SolvingArray, (N-2) * Dim, (N) * Dim)
    i = N-3

    while i >= 0:
        start = i * Dim
        end = i * Dim + 2 * Dim        
        Exchange(SolvingArray, start + Dim, end)        
        MakeDiagFromT(SolvingArray, start, end)        
        i -= 1  
    #Transformation of parameters back to the y, y' basis
    i = 0
    Ps = []
    #calculation of fundamental system P(x)
    while i<N:
        Sol = SolvingArray[i * 8:(i + 1) * 8, 2 * 8]
        Ps.append(Sol)      
        i += 1
    return Ps #return the initial values of each segment,  PARAMETERS
'''

def Solve_One_Segment_Singlegas(Bs, Cs, Ls, Ss, Gs, As):
    """
    Solves the linear system presented in the user guide to obtain the list of integration constants which satisfy the
    imposed boundary conditions for one segment in the single-gas model.\n

    Parameters:
    -----------
        :param Bs: (ndarray) : Matrix for equation y' = By + c
        :param Cs: (ndarray) : Vector for equation y' = By + c
        :param Ls: (float) : Length of the segment  [m]
        :param Ss: (list) : Punctual pumping speeds [m**3/s]
        :param gs: (list) : Punctual gas sources
        :param As: (ndarray) : Specific conductances
    Returns:
    --------
        :param  Ps: (list) :  Integration constants which satisfy the imposed boundary conditions.
    """

    #Similiar to multi segment singlas gas 
    #Solving array has slightly new structure and smaller size: dim = (8,8) with seperate rhs: (8,1)
    # SolvingArray = [Top
    #                 Bottom ]
    #using np.linalg.solve (not the modified echelon algorithmus, with diagonalizing the matrix)
    coeff = [[As[0], Bs[0], Cs[0]]]
    xinit = 0
    Ls2 = Ls
    Top = (np.bmat( [[(alpha(coeff[0], xinit) * Ss[0]*0.5 - As[0]*alpha_prime(coeff[0], xinit))* np.identity(4), (beta(coeff[0], xinit) * Ss[0] * 0.5 - As[0] * beta_prime(coeff[0], xinit))* np.identity(4)]])).reshape((4,8)) 
    Top_rhs = (-Ss[0]*0.5*gamma(coeff[0], xinit) + Gs[0]*0.5 + As[0]*gamma_prime(coeff[0], xinit)).reshape((4,1))

    Bottom = np.bmat( [[(alpha(coeff[-1], Ls2[-1])*Ss[-1]*0.5 + As[-1]*alpha_prime(coeff[-1], Ls2[-1]))*np.identity(4), (beta(coeff[-1], Ls2[-1])*Ss[-1]*0.5 + As[-1]*beta_prime(coeff[-1], Ls2[-1]))*np.identity(4)]])
    Bottom_rhs = (-Ss[-1]*0.5*gamma(coeff[-1], Ls2[-1]) + Gs[-1]*0.5 - As[-1]*gamma_prime(coeff[-1], Ls2[-1])).reshape((4,1))

    SolvingArray = np.bmat([[Top],[Bottom]])
    rhs = np.bmat([[Top_rhs],[Bottom_rhs]])
    print SolvingArray
    print rhs
    
    Ps = [np.linalg.solve(SolvingArray, rhs)]
    print Ps
    return Ps


    



