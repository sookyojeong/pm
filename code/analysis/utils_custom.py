'''
Created on November 5th, 2019

@author: sookyojeong

contains util functions that are used in different analyses.
'''
# import packages
import os
import pandas as pd
import numpy as np
from openpyxl import load_workbook

'''
regwrite: takes list of strings of y, X, and fixed effect variables, and
make them into a combined string that can be put into regression models.
    -input: list of strings
    -output: string of reg formula
'''
def regwrite(y,X,FE=[]):
    ret = ''
    ret = ret + y + ' ~ ' # add Y
    for v in X:
        ret = ret + v + ' +' # add X's
    if len(FE) != 0:
        for v in FE:
            ret = ret + 'C(' + v + ')' + '+' # add FE's
    ret = ret[:-1] # get rid of the last '+'
    return ret

'''
results2mat: takes dataframe of regression results with 'coef' and 'std err'
columns and returns array of results in table format.
    -input: regression model object, names of endog vars, list of stats you want to add.
    -output: 1d array of results in table format
'''
def results2mat(fit,X,add_stats=['N']):
    ret = [0 for x in range(2*len(X)+len(add_stats))]
    counter = 0
    tab_reg=pd.read_html(fit.summary().tables[1].as_html(),header=0,index_col=0)[0]
    for v in X: # get coefs and std errs for each x
        ret[counter] = tab_reg.loc[v]['coef']
        ret[counter+1] = tab_reg.loc[v]['std err']
        counter = counter+2
    if 'N' in add_stats:    # add nobs
        ret[counter] = fit.nobs
    return ret
    
'''
save_table: takes array of results, and saves it to sheet in existing table_raw excel file
'''
def mat2table(mat,shname):
    path = '../../output/tables_raw.xlsx'   # path of output excel file
    book = load_workbook(path)
    writer = pd.ExcelWriter(path, engine = 'openpyxl')
    writer.book = book
    
    df = pd.DataFrame(mat) # write mat on table.
    df.to_excel(writer,sheet_name=shname,index=False,header=False)
    writer.save()
    writer.close()
    print('Saved the results to tables_raw sheet: '+shname)

