import numpy as np
import matplotlib.pyplot as plt



def hesgau(x, y, sigma):
    dim = len(x)
    dist = np.sum(np.power(x-y, 2))
    return (dim/sigma - dist/sigma**2)*np.exp(-dist/(2*sigma))

def ff(args):
    return stein_novelty(args[0], args[1], args[2])

def pp(args):
    return args[0].predict([args[1]])[0]


def stein_novelty(point, data_list, sigma):
    n = len(data_list)
    score = 0
    score = np.sum([hesgau(point, data_list[k,:], sigma) for k in range(n)])
    score = score/(n*(n+1)/2)
    return -score


def parallel_graph(args):
    i = args[0]
    xy = args[1]
    n = args[2]
    vl_it_list = args[3]
    sigma = args[4]
    Z = args[5]
    z_list = []

    for j in range(50):
        p = [xy[:,0][j], xy[:,1][i]] 
        z = 0
        for k in range(n):
            z = z + hesgau(p, vl_it_list[k,:], sigma)
        z = z/(n*(n+1)/2)
        z_list.append(z)
    return z_list

def SD(data_list, sigma):
    n = len(data_list)
    if n <= 1:
        return -1
    z0 = 0

    for k in range(n):
        #print(k)
        for l in range(k+1,n):
            z0 = z0 + hesgau(data_list[l,:], data_list[k,:], sigma)
    steind = z0/(n*(n-1)/2.)
    return steind


