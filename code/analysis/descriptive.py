'''
Created on November 4th, 2019

@author: sookyojeong

merge school data with weather & monitoring sites data 
'''
# import packages
import os
import pandas as pd
import numpy as np
from utils_custom import *

def main(input_path):

    # get data in dataframe
    df = pd.read_csv(input_path,encoding='utf-8')
    
    # inititate matrix with width w and height h
    mat = [[0 for x in range(8)] for y in range(5)]
    
    desc_vars = ['PM10_mean_t','wind_t','sco_math_4kp','sco_math_2kp','sco_kor_4kp',
                 'sco_kor_2kp','sco_eng_4kp','sco_eng_2kp']
    
    col = 0
    for v in desc_vars:
        mat[0][col] = df[v].mean()
        mat[1][col] = df[v].std()
        mat[2][col] = df[v].min()
        mat[3][col] = df[v].max()
        mat[4][col] = df[v].shape[0]
        col = col+1
    
    mat2table(mat,'descriptive')
    
    
        