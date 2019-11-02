'''
Created on Apr 2, 2019

@author: sookyojeong
'''

'''
Created on Mar 29, 2019

@author: sookyojeong
'''
import numpy as np
import os
import pandas as pd  
import requests
pd.set_option('display.max_columns',999) 

def rowIndex(row):
    return row.name
     
def geocoder(row):
    r = requests.get('http://api.vworld.kr/req/address?service=address&request=getCoord&type=ROAD&key=66AE5204-E1F6-32A2-B3F3-FAC1E934C9CD&format=json&address='+row['address'])
     
    if (r.json()['response']['status'] == 'OK'):
        print(r.json())
        x = r.json()['response']['result']['point']['x']
        y = r.json()['response']['result']['point']['y']
    else:
        r = requests.get('http://api.vworld.kr/req/address?service=address&request=getCoord&type=PARCEL&key=66AE5204-E1F6-32A2-B3F3-FAC1E934C9CD&format=json&address='+row['address'])
        if (r.json()['response']['status'] == 'OK'):
            print(r.json())
            x = r.json()['response']['result']['point']['x']
            y = r.json()['response']['result']['point']['y']
        else:
            x= ''
            y= ''
    print(row['rowIndex'])
    row['x'] = x
    row['y'] = y
    return row
     
def main(raw_path,clean_path):
    # initiate data objects
    raw = {}
    clean = {}
    years = ['2018','2017','2016','2015','2014','2013']

    for y in years:
        for filename in os.listdir(os.path.join(raw_path,y)):
            
            if not 'DS_Store' in filename:
                # get filename
                name = os.path.splitext(filename)[0]
                print(name)
                                                  
                if filename.endswith(".xlsx"):
                    # read excel files
                    raw[name] = pd.read_excel(os.path.join(raw_path,y,filename));
                elif filename.endswith(".csv"):
                    if (y == '2014' or y=='2016'):
                        raw[name] = pd.read_csv(os.path.join(raw_path,y,filename),encoding='cp949')
                    else:# read csv files
                        raw[name] = pd.read_csv(os.path.join(raw_path,y,filename))
                else:
                    raise ValueError('error: not a data file')
                
                # rename variables
                print(raw[name].columns)
                raw[name] = raw[name].rename(columns = {"지역":"region"+y, "측정소코드":"site_code", \
                                                         "측정소명":"site_name"+y, "측정일시":"time", "주소": "address"+y})
                
                # keep only site info
                raw[name] = raw[name][['site_code','region'+y,'site_name'+y,'address'+y]]
                
                # drop duplicates
                raw[name] = raw[name].drop_duplicates()
                
                # stop if site code has duplicate
                if any(raw[name]['site_code'].duplicated()):
                    raise ValueError('error: duplicate site_code exists')
                
                
    # merge all data in dictionary
    df = pd.DataFrame()
    df = df.append(raw['2013_1'])
    df=df.merge(raw['2014_1'], left_on ='site_code', right_on ='site_code')
    df=df.merge(raw['2015_1'], left_on ='site_code', right_on ='site_code')
    df=df.merge(raw['2016_1'], left_on ='site_code', right_on ='site_code')
    df=df.merge(raw['2017_1'], left_on ='site_code', right_on ='site_code')
    df=df.merge(raw['2018_1'], left_on ='site_code', right_on ='site_code')

    # fill in missing data
    df['region']=np.nan
    df['address']=np.nan
    df['site_name']=np.nan
    for y in years:
        df['region'] = df['region'].fillna(df['region'+y])
        df['address'] = df['address'].fillna(df['address'+y])
        df['site_name'] = df['site_name'].fillna(df['site_name'+y])

    df = df[['site_code','region','address','site_name']]
    df['rowIndex'] = df.apply(rowIndex, axis=1)
    df = df.apply(geocoder,axis=1)

    df.to_csv(clean_path, encoding='utf-8', index=False)
