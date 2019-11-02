'''
Created on Apr 28, 2019

@author: sookyojeong


'''
# import packages
import os
import pandas as pd
import numpy as np
import nltk
from nltk.tokenize import word_tokenize

pd.set_option('display.max_columns',999) 
  
def main(input_x1_schools,input_x1_schools_type,input_x2_schools_basic,input_x2_schools_vars,clean_path):
    df_s = pd.read_csv(input_x1_schools)

    # tokenize address
    df_s['tokenized'] = df_s['schl_address'].apply(word_tokenize)
    df_s['region1'] = df_s['tokenized'].str[0]
    df_s['region2'] = df_s['tokenized'].str[1]
    df_s['region3'] = df_s['tokenized'].str[2]

    # get establishment year
    df_s['establish'] = df_s['설립일자'].astype(str).str[0:4]

    df_t = pd.read_csv(input_x1_schools_type,encoding='utf-8')

    df_s = df_s.merge(df_t, how='left', left_on = ['region1','schl_name'],right_on = ['region','name'],validate='one_to_one')


    # make df_s regname1
    df_s['regname'] = df_s['region1']
    df_s['regname'] = df_s['regname'].replace({'서울특별시':'서울','경기도':'경기','경상남도':'경남','경상북도':'경북',\
                              '부산광역시':'부산', '전라남도':'전남', '전라북도':'전북','인천광역시':'인천',\
                              '충청남도':'충남','강원도':'강원','대구광역시':'대구','충청북도':'충북',\
                              '광주광역시':'광주', '대전광역시':'대전','울산광역시':'울산','제주특별자치도':'제주',\
                              '세종특별자치시':'세종'})

    # make df_s regname_sub
    df_s['region2_type']=df_s['region2'].astype(str).str[-1:]
    df_s['regname_sub'] = ''
    df_s['regname_sub'] = df_s[(df_s['region2_type']!='동')&(df_s['region2_type']!='면')\
                               &(df_s['region2_type']!='읍')]['region2']
    df_s['regname_sub'] = df_s['regname_sub'].fillna(df_s['region1'])

    # select columns
    df_s = df_s[['schl_id','schl_name','type','schl_address','x','y','establish','regname','regname_sub','students_num_16','teachers_num_16','class_num_16']]

    # make variable names consistent
    df_s = df_s.rename(columns={'teachers_num_16':'nteacher', 'students_num_16':'nstudent','class_num_16':'nclass'})
    df_s['regname1'] = df_s['regname']

    ## read in main data
    df_m = input_x2_schools_basic,encoding='cp949')
    df_m = df_m[df_m['schlevelname']=='고등학교']
    df_m = df_m[df_m['year']==2016]

    # merge with nclass, nstudent info
    df_v = pd.read_csv(input_x2_schools_vars,encoding='cp949')
    df_v = df_v[df_v['schlevelname']=='고등학교']
    df_v = df_v[df_v['year']==2016]

    df_v = df_v.replace({" ":np.nan})
    df_v = df_v.dropna(how='all',axis=1)
    filter_col1 = [col for col in df_v if col.startswith('tearank_')]
    filter_col2 = [col for col in df_v if col.startswith('numcls_')]
    df_v = df_v[['schid']+filter_col1+filter_col2]

    df_m = df_m.merge(df_v, on=['schid'],how='left',validate='one_to_one')
    df_m['nteacher'] = df_m[filter_col1].replace({np.nan:0}).astype(int).sum(axis=1)
    df_m['nstudent'] = df_m[['numcls_m1','numcls_f1','numcls_m2','numcls_f2','numcls_m3','numcls_f3']].replace({np.nan:0}).astype(int).sum(axis=1)
    df_m['nclass'] = df_m[['numcls_1','numcls_2','numcls_3']].replace({np.nan:0}).astype(int).sum(axis=1)
    df_m = df_m.drop(columns = filter_col1+filter_col2)

    # clean variables
    df_m['establish'] = df_m['establish'].astype(str)
    # clean regname1, regname_sub, regtypename
    #replace '안양?과' to '안양시'
    df_m['regname_sub'] = df_m['regname_sub'].replace({'안양?과':'안양시'})
    df_m['regname_sub_type']=df_m['regname_sub'].astype(str).str[-1:]
    # get school type (일반고,특성화고,자율고,특수목적고)
    df_m['type'] = df_m['hightypename']
    df_m['type'] = df_m['type'].replace({'특성화고(직업)':'특성화고','특목고':'특수목적고','특성화고(대안)':'특성화고',\
                                        '특성화':'특성화고'})


    # get only unique values for main data as well
    set = {}
    set[0] = ['regname','establish']
    set[1] = ['regname','establish','type']
    set[2]= ['regname','type','regname_sub']
    set[3] = ['regname','establish','regname_sub']
    set[4] = ['regname','establish','type','regname_sub']

    set[5] = ['regname1','establish']
    set[6] = ['regname1','establish','type']
    set[7] = ['regname1','type','regname_sub']
    set[8] = ['regname1','establish','regname_sub']
    set[9] = ['regname1','establish','type','regname_sub']

    set[10] = ['regname','regname_sub','type','nclass']
    set[11]= ['regname','regname_sub','type','nclass','nteacher']
    set[12]= ['regname','regname_sub','type','nstudent','nclass','nteacher']
    set[13]= ['regname','regname_sub','type','nclass']
    set[14] = ['regname','regname_sub','establish','nclass']
    set[15]= ['regname','regname_sub','establish','type']
    set[16]= ['regname','regname_sub','establish','type','nclass']
    set[17]= ['regname','regname_sub','establish','type','nclass','nteacher']
    set[18] = ['regname','regname_sub','establish','type','nstudent','nclass','nteacher']

    set[19] = ['regname1','regname_sub','type','nclass']
    set[20]= ['regname1','regname_sub','type','nclass','nteacher']
    set[21]= ['regname1','regname_sub','type','nstudent','nclass','nteacher']
    set[22]= ['regname1','regname_sub','type','nclass']
    set[23] = ['regname1','regname_sub','establish','nclass']
    set[24]= ['regname1','regname_sub','establish','type']
    set[25]= ['regname1','regname_sub','establish','type','nclass']
    set[26]= ['regname1','regname_sub','establish','type','nclass','nteacher']
    set[27]= ['regname1','regname_sub','establish','type','nstudent','nclass','nteacher']


    df_mh={}
    df_sh={}
    df_hh={}
    for i in range(28):
        df_mh[i] = df_m.drop_duplicates(set[i])
        df_sh[i] = df_s.drop_duplicates(set[i])
        df_hh[i] = df_mh[i].merge(df_sh[i],on=set[i],how='inner',validate='one_to_one')
        df_hh[i] = df_hh[i][['schid','schl_id']]
        df_hh[i] = df_hh[i].rename(columns = {'schl_id':'schl_id'+str(i)})
        df_m = df_m.merge(df_hh[i],how='left',on='schid',validate='one_to_one')


    df_m['schl_id'] = df_m['schl_id27']
    for i in (reversed(range(27))):
        df_m['schl_id'] = df_m['schl_id'].fillna(df_m['schl_id'+str(i)])
        df_m['flag']=1
        for j in range(i+1,28):
            df_m.loc[df_m['schl_id'+str(j)].isna()==False]['flag']= 0

        df_m.loc[(df_m['schl_id'].duplicated(keep=False)==True)&(df_m['schl_id'].isna()==False)&(df_m['flag']==1)]=np.nan
        assert df_m[(df_m['schl_id'].duplicated(keep=False)==True)&(df_m['schl_id'].isna()==False)].shape[0]==0

    df_m = df_m[['schid','schl_id']]

    # save
    df_m.to_csv(clean_path,encoding='utf-8',index=False)
