'''
Created on November 4th, 2019

@author: sookyojeong

merge school data with weather & monitoring sites data 
'''
# import packages
import os
import pandas as pd
import numpy as np
import statsmodels.formula.api as sm
from utils_custom import *


def main(input_path):

    # get data in dataframe
    df = pd.read_csv(input_path,encoding='utf-8')
    
    outcomes = ['sco_math_4kp','sco_math_2kp','sco_kor_4kp', 'sco_kor_2kp','sco_eng_4kp','sco_eng_2kp']
    xvars = ['PM10_mean_t', 'metro', 'reg', 'female', 'educcol','inc_median']
    add_stats=['N']

    # inititate matrix with width w and height h
    mat = [0 for x in range(2*len(xvars)+len(add_stats))]
        
    reg_fits = {}
    for v in outcomes:  # iterate thorugh each outcome and store results
        reg_fits[v] = sm.ols(formula = regwrite(y=v,X=xvars,FE=['year']),data=df).fit()
        mat = np.vstack((mat, results2mat(reg_fits[v],xvars,add_stats)))
    
    # save reg results
    mat = np.transpose(mat[1:])
    mat2table(mat,'ols')
    
    
        