# BLOX
Python implementation of BoundLess Objective-free eXploration (BLOX) for discovery of out-of-trend materials using Stein novelty. 

## Requirements
- Python > 3.5

## Installation
Download or clone the github repository, e.g. git clone https://github.com/tsudalab/BLOX

## Usage
- Preparation
  - feature_list_of_observed_data.csv: Feature list of the observed materials. As an example, morgan fingerprints of 10 ZINC molecules are prepared. 
  - properties_of_observed_data.csv: List of the observed properties by experiment or simulation. The lenghts of "feature_list_of_observed_data.csv" and "properties_of_observed_data.csv" should be the same. Here, we prepared 3 properties: 1 absorption wavelength, 2 intesity, and 3 molecular weight data. The absorption wavelength and intensity data were calculated by DFT simulations.
  - feature_list_of_unchecked_data.csv: Feature list of the unchecked materials. Here, we prepared morgan fingerprints of 100 ZINC molecules.
  - properties_of_unchecked_data.csv: Please note that these data are not prepared in actual situation. Here, to demonstrate BLOX, we calculated absorption wavelength, intesity, and molecular weight data of the unchecked data in advance.

- Exploration by BLOX
  - `python explore_by_BLOX.py feature_list_of_observed_data.csv feature_list_of_unchecked_data.csv properties_of_observed_data.csv --prediction_model RF --iteration_num 20 --dimension 2`
  - The plotted image of observed data and recommended data is saved in the fig directory.
  - Prediction model can be set as '--prediction model RF' for random forest.  
  - The kernel parameter of the kernelized Stein discrepancy can be set as '--sigma XX' without '--adaptive' option.
  - If the dimension is set as 2 (--dimension 2), the absorption wavelength and intensity properties are used for exploration. If the parameter is set as 3, all 3 properties are used. 


- Recommend the next candidate by Stein novelty
  - `python recommend_next_data.py feature_list_of_observed_data.csv feature_list_of_unchecked_data.csv properties_of_observed_data.csv --dimension 2`
  - The recommend candidate and its predicted properties are saved in "recommend_data_by_Stein_novelty.csv".

## Reference
