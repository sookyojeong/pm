'''
Created on November 4th, 2019

@author: sookyojeong

merge school data with weather & monitoring sites data 
'''
# import packages
import os
import pandas as pd
import numpy as np

def sample_flag(df,fvar):
    # initiate series that flags where fvar is nonmissing
    df['ser'] = pd.Series(1, index = df.index)
    df.loc[df[fvar].isna()==True,'ser'] = 0
    # make balanced sample
    df['count'] = df[df.ser==1].groupby('schid')['schid'].transform('count')
    df.loc[df['count']!=8,'ser']=0
    assert all(df[df['ser']==1].groupby(['schid']).agg(['count'])==8)==True
    return df['ser']

# def convert_winddir(v):
    
def main(input_path,output_path):

    # get the crosswalk for school/weather/pollutant sites
    df = pd.read_csv(input_path,encoding='utf-8')
    
    # make balanced sample
    df['s_pm10'] = sample_flag(df,'PM10_mean_06')
    df = df[df['s_pm10']==1]

    # make the wind direction variables
    wind_col = [col for col in df if col.startswith('wind_dir_')]
    for v in wind_col:
        print(v)
        vname = 'wind_'+ v[9:]
        df[vname] = df[v]
        df.loc[((df[v]>=0) & (df[v]<90)), vname] = df[vname]+360
        df[vname] = (df[vname]-270).abs()
        
    # get dummies for school type and metro
    df['reg'] = (df['type']=='일반고').astype(int)
    df['metro'] = (df['regname'].isin(['경기','서울시','인천시','광주시','울산시','부산시','대전시','대구시'])).astype(int)
    
    # make share movein and share moveount variables
    df['moveinp'] = df['movein']/df['nstudent']
    df['moveoutp'] = df['moveout']/df['nstudent']
    
    # college entrance exam variables
    # low performance: 7,8,9
    # high performance: 1,2
    for s in ['kor','eng','math']:
        df['low'+s] = df[s+'p_7']+df[s+'p_8']+df[s+'p_9']
        df['high'+s] = df[s+'p_1']+df[s+'p_2']
        
    # make sample flag variables
    df['s_cexam'] = sample_flag(df,'mathp_1')   # college entrance exam analysis
    df['s_cday'] = sample_flag(df,'clsday_2')   # class days analysis
    df['s_move'] = sample_flag(df,'movein')     # share move in/out analysis
    
    # get month of exam variables
    for var in ['wind','PM10_mean','PM10_median']:
        df[var+'_t'] = df[var+'_06'] 
        df.loc[((df.year==2010)|(df.year==2011)),var+'_t']=df[var+'_07']
        df.loc[(df.year==2009),var+'_t']=df[var+'_10']
    
    # save
    df.to_csv(output_path)