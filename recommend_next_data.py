import numpy as np
import pickle
import matplotlib
import matplotlib.pyplot as plt
from sklearn.svm import SVR
from sklearn import linear_model
from sklearn.ensemble import RandomForestRegressor
#import xgboost as xgb
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from multiprocessing import Pool
import copy as cp
import random
from sklearn.model_selection import GridSearchCV
import sys, csv, time, argparse
from curiosity_sampling import stein_novelty

def load_data(path, read_header = True):
    f = open(path, 'r')
    data_list = []
    reader = csv.reader(f)
    if read_header:
        header = next(reader)
    for row in reader:
        data_list.append([float(p) for p in row])
    return data_list

def build_model(prediction_model, x_train, y_train):
    if prediction_model == 'RF': 
        params = {'n_estimators':[10, 50, 100]}
        gridsearch = GridSearchCV(RandomForestRegressor(), param_grid=params, cv = 3, scoring="r2", n_jobs=parallel, verbose = 1)
        gridsearch.fit(x_train,y_train)
        model =  RandomForestRegressor(n_estimators = gridsearch.best_params_['n_estimators'])
        model.fit(x_train, y_train)
        #print('Coefficient of determination R^2 (WL):', model.score(x_train, y_train))
        return model

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("features_observed")
    parser.add_argument("features_unchecked")
    parser.add_argument("properties_observed")
    parser.add_argument("--sigma", type = float, default = 0.1)
    parser.add_argument("--dimension", type = int, default = 2)
    args = parser.parse_args()
    features_observed_path = args.features_observed
    features_unchecked_path = args.features_unchecked
    properties_observed_path = args.properties_observed
    sigma = args.sigma
    dimension = args.dimension 

    #Parameters 
    parallel = 2
    prediction_model = 'RF'
    predicted_properties_path = 'predicted_properties_of_unchecked_data.csv'
    sn_score_path = 'Stein_novelties_of_unchecked_data.csv'
    recommended_data_path = 'recommend_data_by_BLOX.csv'

    #Load data
    features_observed = np.array(load_data(features_observed_path, read_header = False))
    features_unchecked = np.array(load_data(features_unchecked_path, read_header = False))
    properties_observed = np.array(load_data(properties_observed_path, read_header = True))[:,:dimension]
    if len(features_observed) != len(properties_observed):
        print('Error of observed data size')
        sys.exit()


    #Preparation of data    
    #dimension = len(properties_observed[0]) 
    sc = StandardScaler()
    sc.fit(features_observed)
    sc_features_observed = sc.transform(features_observed)
    sc_features_unchecked = sc.transform(features_unchecked)
    sc_property = StandardScaler() 
    sc_property.fit(properties_observed)
    sc_properties_observed = sc_property.transform(properties_observed)


    #Build prediction model
    model_list = []
    for d in range(dimension):
        model = build_model(prediction_model, sc_features_observed, properties_observed[:,d])
        model_list.append(model)

    #Predict properties of unchecked data (features)
    predicted_properties_list = []
    for d in range(dimension):
        predicted_properties_list.append(model_list[d].predict(sc_features_unchecked))
    predicted_properties_list = np.array(predicted_properties_list).T

    #Save Predicted properties
    with open(predicted_properties_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['absorption wavelength', 'intensity'])
        for vl_it in predicted_properties_list:
            writer.writerow(vl_it)
    
    #Calc. Stein Novelty
    sc_predicted_properties_list = sc_property.transform(predicted_properties_list) 
    sn_data = [stein_novelty(point, sc_properties_observed, sigma=1) for point in sc_predicted_properties_list]

    #Save Stein novelty scores
    out_f = open(sn_score_path, 'w')
    for data in sn_data:
        out_f.write(str(data))
        out_f.write('\n')
    out_f.close()
    
    #Select and save next candidate
    maximum_index = np.argmax(sn_data)
    
    with open(recommended_data_path, 'w') as f:
        f.write('Index of the recommended data in unchecked data list,'+str(maximum_index)+'\n')
        f.write('Predicted properties of the recommended data,'+str(predicted_properties_list[maximum_index])+'\n')
        f.write('Stein novelty score of the recommended data,'+str(sn_data[maximum_index])+'\n')
        f.write('Feature of the recommended data,'+str(features_unchecked[maximum_index]))
      
