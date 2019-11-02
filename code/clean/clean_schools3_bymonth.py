'''
Created on Apr 28, 2019

@author: sookyojeong

merge school data with weather & monitoring sites data 
'''
# import packages
import os
import numpy as np
import pandas as pd
import math

pd.set_option('display.max_columns',999) 
pd.set_option('display.max_rows',999) 

def fillvalues(row,var):
    # if value is null, fill it
    if ((math.isnan(row[var+'0'])==True)&(math.isnan(row[var])==False)):
        # set flag_temp to one
        print(row[var])
        return row[var], 1
    return row[var+'0'],0

def main(input_schools,input_schools_dist,input_college,input_chemical,input_weather,input_region,input_region_demo,clean_path):
    # get the crosswalk for school/weather/pollutant sites
    df_x = pd.read_csv(input_schools_dist,encoding='utf-8')

    # merge it with school info
    df_s = pd.read_csv(input_schools,encoding='utf-8')
    df = df_s.merge(df_x, on='schid',validate='many_to_one',how='left')
    df[['hmin1','hmin2','hmin3','hmin4','hmin5']] = df[['hmin1','hmin2','hmin3','hmin4','hmin5']].fillna(-999).astype(int)

    # merge with college entrance exam info
    df_ce = pd.read_csv(input_college, encoding='utf-8')
    df = df.merge(df_ce, on=['schid','year'] ,validate='one_to_one',how='left')

    # chemical info
    df_v = {}
    cols = {}
    df_v['m'] = pd.read_csv(input_chemical).rename(columns = {'site_code':'msite_code'})
    cols['m'] = ['msite_code']+[col for col in df_v['m'] if col.startswith('PM10_mean')]
    cols['m'] = ['msite_code']+[col for col in df_v['m'] if col.startswith('PM10_')]+[col for col in df_v['m'] if col.startswith('CO_')]+\
     [col for col in df_v['m'] if col.startswith('SO2_')]+[col for col in df_v['m'] if col.startswith('O3_')]+\
     [col for col in df_v['m'] if col.startswith('NO2_')]
    df_v['m'] = df_v['m'][cols['m']+['year']]

    df_v['w'] = pd.read_csv(input_weather)
    cols['w'] = ['wsite_code']+[col for col in df_v['w'] if col.startswith('wind_dir')]
    df_v['w'] = df_v['w'][cols['w']+['year']]

    df_v['h'] = pd.read_csv(input_region)
    df_v['h'].hsite_code = df_v['h'].hsite_code.astype(int)
    cols['h'] = ['inc_min','inc_mean','inc_median','inc_max','hsite_code']
    df_v['h'] = df_v['h'][df_v['h']['year']>2008][cols['h']+['year']]

    df_v['d'] = pd.read_csv(input_region_demo)
    df_v['d'] = df_v['d'][df_v['d']['year']>2008]
    cols['d'] = ['female','educcol','age','dsite_code']
    df_v['d'] = df_v['d'][['year']+cols['d']]

    for t in cols.keys():
        for v in cols[t]:
            df[v+str(0)]=np.nan

    for t in ['m','w','h','d']:
        df['flag']=0
        df['flag_temp']=0
        # merge in chemical info to school data
        for i in range(1,5):
            print(i)
            if ('d' in t):
                df = df.rename(columns={'hmin'+str(i):'dmin'+str(i)})
            df.loc[df[t+'min'+str(i)].isna()==True,t+'min'+str(i)]=-999
            df[t+'min'+str(i)] = df[t+'min'+str(i)].astype(int)
            df = df.merge(df_v[t],how='left',validate='many_to_one',right_on=[t+'site_code','year'],\
                            left_on=[t+'min'+str(i),'year'])
            # fill in na values if it hasn't been filled
            for c in cols[t]:
                print(c)
                # if flag is zero, fill it with values
                df[c+'0'], df['flag_temp'] = zip(*df.apply(lambda x: fillvalues(x,c) if x.flag==0 else (x[c+'0'],x.flag_temp), axis=1))
                df = df.drop(columns =c)
            # if flag_temp is one, set flag to one.
            df.loc[df.flag_temp==1,'flag']=1
        for c in cols[t]:
            df = df.rename(columns = {c+'0':c})


    df.to_csv(clean_path,encoding='utf-8',index=False)

    # #Temp Check
    # df['wind_dir'] = df['wind_dir_06']
    # df.loc[((df['wind_dir']>=0) & (df['wind_dir']<90)), 'wind_dir'] = df['wind_dir']+360
    # df.wind_dir = np.abs(df.wind_dir-270)
    #
    # df['region'] = df['address1_x'].str.split(expand=True)[0]
    # df['metro'] = df['region'].isin(['경기도','서울특별시','부산광역시','대구광역시','인천광역시','광주광역시','대전광역시','울산광역시']).astype(int)
