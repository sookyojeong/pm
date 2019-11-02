'''
Created on Apr 12, 2019

@author: sookyojeong
'''
import requests
import json
import os
import pandas as pd 
import numpy as np
from math import *
pd.set_option('display.max_columns',999) 

# get name, address, and distance to each geo-points

def get_distance(x1,y1,x2,y2):
    R=6373.0
    
    lat1 = float(radians(x1))
    lon1 = float(radians(y1))
    lat2 = float(radians(x2))
    lon2 = float(radians(y2))
    dlon = lon2-lon1
    dlat = lat2-lat1  
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R*c

def rid_min(row):
    row[row['min']]=np.nan
    return row

def main(input_schools,input_chem_sites,input_w_sites,input_regions,clean_path):
    df_s = pd.read_csv(input_schools,encoding='utf-8')
    df_s=df_s[df_s['year']==2016][['schid','address1','latitude','longitude']]
    df_s = df_s.sort_values(by='schid').reset_index()

    ####
    # get monitoring station and its information
    df_m={}
    df_m['m'] = pd.read_excel(input_chem_sites,encoding = 'utf-8')
    df_m['m'] = df_m['m'][['site_code','address','x','y']].rename(columns = {'x':'long','y':'lat','address':'mname','site_code':'msite_code'})

    # get weather station and its information
    df_m['w'] = pd.read_csv(input_w_sites,encoding='utf-8').rename(columns={'wsite_name':'wname','wlong':'long','wlat':'lat'})
    df_m['w'] = df_m['w'][df_m['w']['year']==2017][['wsite_code','wname','lat','long']]

    # get income regions
    df_m['h'] = pd.read_csv(input_regions).rename(columns={'address':'hname','x':'lat','y':'long'})
    df_m['h'] = df_m['h'][df_m['h']['year']==2017][['lat','long','hname','hsite_code']]

    df = df_s
    # First merge schools and monitoring stations
    for t in ['m','w','h']:
        print(t)
        merged_df = pd.merge(df_s.assign(_=1),df_m[t].assign(_=1)).drop('_', axis=1)
        merged_df[['latitude','longitude','lat','long']] = merged_df[['latitude','longitude','lat','long']].astype(float)
        
        # apply your distance function on (lat, long) tuples in the Cartesian product
        merged_df['distance'] = merged_df.apply(lambda x: get_distance(x['latitude'],x['longitude'],x['lat'],x['long']), axis=1)
        
        # pivot table
        dist_matrix = merged_df.set_index(['schid',t+'site_code']).distance.unstack().sort_values(by='schid').reset_index()
        colnames = dist_matrix.columns[1:]
        
        # get min
        for i in range(1,6):
            dist_matrix['min'+str(i)] = dist_matrix[colnames].idxmin(axis=1).astype(int)
            dist_matrix['min'+str(i)+'_d'] = dist_matrix[colnames].min(axis=1)
            # replace nan for the min values
            dist_matrix=dist_matrix.rename(columns = {'min'+str(i):'min'})
            dist_matrix = dist_matrix.apply(rid_min,axis=1)
            dist_matrix=dist_matrix.rename(columns = {'min':t+'min'+str(i),'min'+str(i)+'_d':t+'min'+str(i)+'_d'})
            # replace nan if distance too far
            dist_matrix.loc[dist_matrix[t+'min'+str(i)+'_d']>50,t+'min'+str(i)]=np.nan
            dist_matrix = dist_matrix.merge(df_m[t][[t+'site_code',t+'name']].rename(columns={t+'name':t+'name'+str(i)}), left_on=[t+'min'+str(i)], right_on=[t+'site_code'],how='left', validate='many_to_one')
            dist_matrix = dist_matrix.drop(columns=[t+'site_code'])
        df = df.merge(dist_matrix[['schid',t+'min1',t+'min2',t+'min3',t+'min4',t+'min5',t+'min1_d',t+'min2_d',t+'min3_d',t+'min4_d',t+'min5_d',t+'name1',t+'name2',t+'name3',t+'name4',t+'name5']],on='schid',how='left',validate='one_to_one')


    df.to_csv(clean_path, encoding='utf-8', index=False)
