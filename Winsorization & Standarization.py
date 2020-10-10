# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 10:47:58 2020

@author: SayanPal
"""

#%% Loading All packages
import numpy as np
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Import the Python library for Treasure Data
import os
import warnings
from sklearn.preprocessing import StandardScaler, MinMaxScaler
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings("ignore")

print("\n All Libraries import done")

#%% Importing Datasets
train = pd.read_csv("train_data.csv")
score = pd.read_csv("Score_data.csv")

#%% Reducing DataFrame Size

def reduce_mem_usage(props):
    start_mem_usg = props.memory_usage().sum() / 1024**2 
    print("Memory usage of properties dataframe is :",start_mem_usg," MB")
    for col in props.columns:
        if (props[col].dtype != object) & (props[col].isnull().values.any()==False):  # Exclude strings        
            # make variables for Int, max and min
            mx = props[col].max()
            mn = props[col].min()

            # Make Integer/unsigned Integer datatypes
            if mn >= 0:
                if mx < 255:
                    props[col] = props[col].astype(np.uint8)
                elif mx < 65535:
                    props[col] = props[col].astype(np.uint16)
                elif mx < 4294967295:
                    props[col] = props[col].astype(np.uint32)
                else:
                    props[col] = props[col].astype(np.uint64)
            else:
                if mn > np.iinfo(np.int8).min and mx < np.iinfo(np.int8).max:
                    props[col] = props[col].astype(np.int8)
                elif mn > np.iinfo(np.int16).min and mx < np.iinfo(np.int16).max:
                    props[col] = props[col].astype(np.int16)
                elif mn > np.iinfo(np.int32).min and mx < np.iinfo(np.int32).max:
                    props[col] = props[col].astype(np.int32)
                elif mn > np.iinfo(np.int64).min and mx < np.iinfo(np.int64).max:
                    props[col] = props[col].astype(np.int64)    
        
        # Make float datatypes 32 bit
        else:
            pass            
    
    # Print final result
    print("___MEMORY USAGE AFTER COMPLETION:___")
    mem_usg = props.memory_usage().sum() / 1024**2 
    print("Memory usage is: ",mem_usg," MB")
    print("This is ",100*mem_usg/start_mem_usg,"% of the initial size")
    return props

ttrain = reduce_mem_usage(train)
sscore = reduce_mem_usage(score)

#%% Outlier Treatment - Winsorization (Percentile Capping)
def outlier_generic(df,dept,max_flag=True):
    df_generic = df.copy()
    df_generic = df_generic.drop(columns = dept,axis=1)
    if max_flag:    
        col_list = df_generic.describe().T.loc[df_generic.describe().T["max"]>1].index
    else:
        col_list = df_generic.describe().columns
    
    for num_col in col_list:
        df_generic[num_col] = np.where((df_generic[num_col]>df_generic[num_col].quantile(0.99)), df_generic[num_col].quantile(0.99),df_generic[num_col])
    df_generic = pd.concat([df[[dept]],df_generic],axis =1)    
    return df_generic, col_list

outlier_train, Columns_list = outlier_generic(df = ttrain, dept='dependent_variable_name')
#%% Scaling Standardization 
def scaling_generic(df,l):
    scale_train = df.copy()
    df_generic_features = scale_train[l]
    
    generic_scaler = StandardScaler().fit(df_generic_features.values)
    generic_features = generic_scaler.transform(df_generic_features.values)
    
    scale_train[l]=generic_features
    return scale_train

scaled_train = scaling_generic(df = outlier_train, l = Columns_list)
#%%