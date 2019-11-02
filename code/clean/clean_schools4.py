'''
Created on Apr 28, 2019

@author: sookyojeong

match schools
'''
# import packages
import os
import pandas as pd
import numpy as np
pd.set_option('display.max_columns',999) 


def main(input_basic,input_vars,input_test,input_xwalk,input_geo,clean_path):

    df_b = pd.read_csv(input_basic,encoding='cp949')
    # get highschools only
    df_b = df_b[df_b['schlevelname']=='고등학교']
    # school type
    df_b['type'] = df_b['hightypename']
    df_b['type'] = df_b['type'].replace({'특성화고(직업)':'특성화고','특목고':'특수목적고','특성화고(대안)':'특성화고',\
                                         '특성화':'특성화고'})

    # get school vars
    df_v = pd.read_csv(input_vars,encoding='cp949')
    df_v = df_v[df_v['schlevelname']=='고등학교'].reset_index()

    # move-in and move-out variables are of previous years
    df_v = df_v.sort_values(['schid','year']).reset_index()
    df_v = df_v.rename(columns = {'movein':'movein_temp', 'moveout':'moveout_temp'})
    df_v['movein'] = df_v.groupby('schid')['movein_temp'].apply(lambda x: x.shift(-1))
    df_v['moveout'] = df_v.groupby('schid')['moveout_temp'].apply(lambda x: x.shift(-1))
    df_v = df_v.drop(columns = ['movein_temp','moveout_temp'])

    # replace all space values to NaN
    df_v = df_v.replace({" ":np.nan})
    df_v = df_v.dropna(how='all',axis=1)

    # health cols (grades)
    healthcols = []
    for i in range(1,4):    # grade
        for j in range(1,6): # health levels
            varname = 'health_gd'+str(i)+'_g'+str(j)
            df_v[varname] = df_v['health_m_gd'+str(i)+'_g'+str(j)]+df_v['health_fe_gd'+str(i)+'_g'+str(j)]
            healthcols.append(varname)
            
    # get school test vars
    df_t = pd.read_excel(input_test)
    df_t = df_t.rename(columns = {'기준년도':'year'})

    # get crosswalk
    df_x = pd.read_csv(input_xwalk,encoding='utf-8')
    df_x = df_x[df_x.schid.isna()==False]

    # get crosswalk lat long info
    df_s = pd.read_excel(input_geo,encoding='cp949')
    df_s = df_s[df_s['학교급구분'] == '고등학교'] # restrict to high schools (change this to elem/middle)
    df_s = df_s.rename(columns={'학교ID':'schl_id'})
    # drop extra variables
    df_s = df_s.drop(columns = ['학교급구분','본교분교구분','운영상태','시도교육청코드','시도교육청명',\
                                '교육지원청코드','교육지원청명','생성일자','변경일자','데이터기준일자',\
                                '제공기관코드','제공기관명'])

    # merge school info
    df = df_b.merge(df_v, on=['year','schid'],how='outer',validate='one_to_one')
    df = df.merge(df_t,on=['year','schid'], how='outer', validate='one_to_one')
    df = df.merge(df_x,on='schid',how='left',validate='many_to_one')
    df = df.merge(df_s,on='schl_id',how='left',validate='many_to_one')

    # restrict to those who were matched
    df = df[df['schl_id'].isnull()==False]

    # sample restriction
    df = df[df['sco_math_4kp'].isna()==False]
    df = df[df['schl_id'].isna()==False]
    df['year']=df['year'].astype(int)
    df = df[(df['year']<2017) & (df['year']>=2009)]

    #balance
    df_minmax = df.groupby(['schid'])['year'].agg(['min','max','size']).reset_index()
    df = df.merge(df_minmax, on = 'schid', how='left', validate='many_to_one')
    df = df[df['size']==8]

    filter_col = [col for col in df if col.startswith('tearank_')]
    df['nteacher'] = df[filter_col].replace({np.nan:0}).astype(int).sum(axis=1)
    df['nstudent'] = df[['numcls_m1','numcls_f1','numcls_m2','numcls_f2','numcls_m3','numcls_f3']].replace({np.nan:0}).astype(int).sum(axis=1)
    df['nclass'] = df[['numcls_1','numcls_2','numcls_3']].replace({np.nan:0}).astype(int).sum(axis=1)

    #rename variables
    df = df.rename(columns = {'학교명':'schname','설립일자':'establish','설립형태':'public',\
                                  '소재지지번주소':'address1','소재지도로명주소':'address2',\
                                  '위도':'latitude','경도':'longitude',\
                                  'regname_x':'regname','regname_sub_x':'regname_sub'})

    sco_col = [col for col in df if col.startswith('sco_')]
    cols = ['year','schid','establish', 'type',
            'nstudent','nclass','movein','moveout','numdrop',
            'nteacher','clsday_1','clsday_2','clsday_3','clsday_7','clsday_8',
            'latitude','longitude','address1', 'address2','schname','regname','regname_sub']
    df = df[cols+sco_col+healthcols]

    df.to_csv(clean_path,encoding='utf-8')
