import numpy as np
import pickle
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from multiprocessing import Pool
import copy as cp
import csv
import argparse
from curiosity_sampling import stein_novelty

def load_data(path):
    f = open(path, 'r')
    data_list = []
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        data_list.append([float(p) for p in row])
    return data_list

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("data")
    parser.add_argument("point")
    parser.add_argument("output")
    parser.add_argument("--sigma", type = float, default = 0.1)
    parser.add_argument("--adaptive", action='store_true')
    args = parser.parse_args()
    data_path = args.data
    point_path = args.point
    output_path = args.output
    sigma = args.sigma
    adaptive = args.adaptive

    #Load data
    input_data = np.array(load_data(data_path))
    point_data = np.array(load_data(point_path))

    if adaptive:
        sc = StandardScaler()
        sc.fit(input_data)
        input_data = sc.transform(input_data) 
        point_data = sc.transform(point_data)
        sigma = 1

    #Calc. Stein Novelty
    sn_data = [stein_novelty(point, input_data, sigma) for point in point_data]
    
    #Save Stein novelty scores
    out_f = open(output_path, 'w')
    for data in sn_data:
        out_f.write(str(data))
        out_f.write('\n')
    out_f.close()
