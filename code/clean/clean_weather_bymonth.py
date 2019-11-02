'''
Created on Apr 7, 2019

@author: sookyojeong
'''


import os
import pandas as pd  
pd.set_option('display.max_columns',999) 
import numpy as np

def main(raw_path, site_path, clean_path):
    df = pd.read_csv(raw_path,encoding='cp949')

    # rename variables
    df = df.rename(columns = {"지점":"wsite_code", "일시":"date", "평균기온(°C)":"avg_temp",\
             "평균풍속(m/s)": "avg_windv", "최다풍향":"wind_dir", "최고기온(°C)": "max_temp",\
             "최저기온(°C)":"min_temp", "일최다강수량(mm)":"max_precip","최대풍속(m/s)":"max_windv",\
             "최대풍속 풍향(16방위)":"max_windv_dir"})
    df = df[['wsite_code', 'date', 'avg_temp','avg_windv','wind_dir',"max_temp","min_temp",\
             "max_precip","max_windv","max_windv_dir"]]

    # make year month variable
    df['date'] = df['date'].apply(str)
    df['year'] = df['date'].str.slice(start=0,stop=4).astype(int)
    df['month'] = df['date'].str.slice(start=5,stop=7)

    # restrict the years
    df = df[(df['year']>=2008)&(df['year']<=2018)]

    # do wind_dir for now
    df= df.pivot_table(index=['wsite_code','year'],columns = 'month',values='wind_dir').reset_index()
    for i in ["01","02","03",'04','05','06','07','08','09','10','11','12']:
        df = df.rename(columns = {i:'wind_dir_'+str(i)})
        
    # get yearly avg
    cols = [col for col in df if col.startswith('wind_dir_')]
    df['wind_dir_ymode'] = df[cols].mode(numeric_only=True, axis=1).mean(numeric_only=True,axis=1)
    df['wind_dir_ymean'] = df[cols].mean(numeric_only=True, axis=1)

    # import site data
    df2 = pd.read_csv(site_path,encoding='cp949')

    # rename variables
    df2 = df2.rename(columns = {"지점":"wsite_code", "지점명":"wsite_name","위도":"wlat","경도":"wlong" })
    df2 = df2[['wsite_code','wsite_name','wlat','wlong']]
    df2 =  df2[~df2['wsite_code'].duplicated(keep='first')]

    df = df.merge(df2, on ='wsite_code', validate='many_to_one')
    df.to_csv(clean_path, encoding='utf-8', index=False)
