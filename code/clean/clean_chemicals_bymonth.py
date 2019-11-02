'''
Created on Mar 29, 2019

@author: sookyojeong
'''

import os
import pandas as pd  
import numpy as np
pd.set_option('display.max_columns',999) 
pd.set_option('display.max_rows', 500)

# set directory                   

def main(raw_path,clean_path):
    # raw dir: ../../data/raw/
    # clean dir: ../../data/clean/monitorClean_bymonth.csv
    
    # initiate data objects
    raw = {}
    clean = {}
    for y in range(2009,2017):
        for filename in os.listdir(os.path.join(raw_path,str(y))):
            
            if not 'DS_Store' in filename:
                # get filename
                name = os.path.splitext(filename)[0]
                print(name)
                                                  
                if filename.endswith(".xlsx"):
                    # read excel files
                    raw[name] = pd.read_excel(os.path.join(root,'raw',str(y),filename));
                elif filename.endswith(".csv"):
                    if (y == 2014 or y==2016):
                        raw[name] = pd.read_csv(os.path.join(root,'raw',str(y),filename),encoding='cp949')
                    else:# read csv files
                        raw[name] = pd.read_csv(os.path.join(root,'raw',str(y),filename))
                else:
                    raise ValueError('error: not a data file')
                
                # rename variables
                raw[name] = raw[name].rename(columns = {"지역":"region", "측정소코드":"site_code", \
                                                         "측정소명":"site_name", "측정일시":"time", "주소": "address"})
                # display time range
                print(raw[name]['time'].min(),raw[name]['time'].max())
                
                # break time variable
                raw[name]['time'] = raw[name]['time'].apply(str)
                raw[name]['year'] = raw[name]['time'].str.slice(start=0,stop=4)
                raw[name]['month'] = raw[name]['time'].str.slice(start=4,stop=6)
                
                # replace missings
                chemicals = ['CO','NO2','O3','PM10','PM25','SO2']
                for c in chemicals:
                    if c in raw[name].columns:
                        raw[name] = raw[name].replace({c:-999},np.nan)

    # append all data in dictionary
    df = pd.DataFrame()
    for key in raw:
        df = df.append(raw[key])

     # the dataset is in hour units. Change it to month.
    df = df.groupby(['site_code','year','month'])\
            ['SO2','CO','O3','NO2','PM10','PM25'].agg(['min','max','mean','median']).reset_index()
    # flatten column name
    df.columns = pd.Index([e[0]+"_"+e[1] for e in df.columns])
    df = df.rename(columns = {'site_code_':'site_code', 'year_':'year','month_':'month'})

    # do PM10s for now.
    filter_col = [col for col in df if col.startswith('PM10')]+\
    [col for col in df if col.startswith('CO')] + [col for col in df if col.startswith('NO2')]+\
    [col for col in df if col.startswith('O3')] + [col for col in df if col.startswith('PM25')]+\
    [col for col in df if col.startswith('SO2')]
    df= df.pivot_table(index=['site_code','year'],columns = 'month',values=filter_col)
    df.columns = pd.Index([e[0]+"_"+str(e[1]) for e in df.columns])
    df = df.reset_index()

    # get yearly average
    for s in ['min','mean','median','max']:
        for c in ['PM10_','CO_','NO2_','O3_','PM25_','SO2']:
            cols = [col for col in df if col.startswith(c+s)]
            df[c+s+'_yr'] = df[cols].mean(numeric_only=True, axis=1)

    # save
    df.to_csv(clean_path), index=False)
