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
from recommend_next_data import load_data

def build_model(prediction_model, x_train, y_train):
    if prediction_model == 'RF': 
        params = {'n_estimators':[10, 50, 100]}
        gridsearch = GridSearchCV(RandomForestRegressor(), param_grid=params, cv = 3, scoring="r2", n_jobs=parallel, verbose = 1)
        gridsearch.fit(x_train,y_train)
        model =  RandomForestRegressor(n_estimators = gridsearch.best_params_['n_estimators'])
        model.fit(x_train, y_train)
        #print('Coefficient of determination R^2 (WL):', model.score(x_train, y_train))
        return model

def recommend_next(prediction_model, features_observed, features_unchecked, properties_observed):

    #Preparation of data    
    dimension = len(properties_observed[0]) 
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
    if adaptive:
        sc_predicted_properties_list = sc_property.transform(predicted_properties_list) 
        sn_data = [stein_novelty(point, sc_properties_observed, sigma=1) for point in sc_predicted_properties_list]
    else:
        sn_data = [stein_novelty(point, sc_properties_observed, sigma) for point in predicted_properties_list]

    #Save Stein novelty scores
    out_f = open(sn_score_path, 'w')
    for data in sn_data:
        out_f.write(str(data))
        out_f.write('\n')
    out_f.close()
    
    #Select and save next candidate
    maximum_index = np.argmax(sn_data)
    
    return maximum_index, predicted_properties_list[maximum_index], sn_data[maximum_index]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("features_observed")
    parser.add_argument("features_unchecked")
    parser.add_argument("properties_observed")
    parser.add_argument("--sigma", type = float, default = 0.1)
    parser.add_argument("--adaptive", action='store_true')
    parser.add_argument("--prediction_model", default = 'RF')
    parser.add_argument("--iteration_num", type = int, default = 20)
    args = parser.parse_args()
    features_observed_path = args.features_observed
    features_unchecked_path = args.features_unchecked
    properties_observed_path = args.properties_observed
    sigma = args.sigma
    adaptive = args.adaptive
    prediction_model = args.prediction_model
    num_loop = args.iteration_num

    #Parameters 
    parallel = 2
    predicted_properties_path = 'predicted_properties_of_unchecked_data.csv'
    sn_score_path = 'Stein_novelties_of_unchecked_data.csv'
    recommended_data_path = 'recommend_data_by_BLOX.csv'
    properties_unchecked_path = 'properties_of_unchecked_data.csv'    


    #Load data
    features_observed = np.array(load_data(features_observed_path, read_header = False))
    features_unchecked = np.array(load_data(features_unchecked_path, read_header = False))
    properties_observed = np.array(load_data(properties_observed_path, read_header = True))
    properties_unchecked = np.array(load_data(properties_unchecked_path, read_header = True))
    if len(features_observed) != len(properties_observed):
        print('Error of observed data size')
        sys.exit()


    for l in range(num_loop):
         print('Exploration:', l)
         recommended_index, predicted_properties, SN = recommend_next(prediction_model, features_observed, features_unchecked, properties_observed)
         print('Recommended_index', recommended_index, 'predicted_properties', predicted_properties, 'Stein novelty', SN)

         #Add the experimental or simulation result of the recommended data
         features_observed = np.append(features_observed, [features_unchecked[recommended_index]], axis = 0)
         properties_observed = np.append(properties_observed, [properties_unchecked[recommended_index]], axis = 0)         

         #Removed the recommend data
         features_unchecked = np.delete(features_unchecked, recommended_index, axis = 0)
         properties_unchecked = np.delete(properties_unchecked, recommended_index, axis = 0)
         
         #Plot data
         plt.scatter(properties_observed[:-1,0], properties_observed[:-1,1], label='Prev data')
         plt.scatter([predicted_properties[0]], [predicted_properties[1]], label='Predicted properties' )
         plt.scatter(properties_observed[-1:,0], properties_observed[-1:,1], label='Experimental data')
         plt.xlabel('Wave length (nm)')
         plt.ylabel('Intensity')
         plt.xlim([100, 500])
         plt.ylim([0,1.5])
         plt.legend()
         plt.savefig('fig/observed_data_iteration'+str(l)+'.png', dpi = 300)
         plt.close()
