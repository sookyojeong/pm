'''
Created on Apr 28, 2019

@author: sookyojeong

'''
# import packages
import os
import pandas as pd
import numpy as np
pd.set_option('display.max_columns',999) 


def main(raw_path, clean_path):
    raw = {}
    # read all highschool info scraped from the internet
    for i in range(0,63):
        raw[i] = pd.read_csv(os.path.join(raw_path,'highschools'+str(i)+".csv"))
        raw[i].shape

    # append all data in dictionary
    df = pd.DataFrame()
    for key in raw:
        df = df.append(raw[key])
        
    # take out parantheses in variables
    internet_vars = ['class_num_17','student_num_17','teacher_num_17',\
                     'class_num_16','student_num_16','teacher_num_16']
    for v in internet_vars:
        df[v] = df[v].str.replace(r"\(.*\)","")
        df[v] = df[v].str.replace(r",","")
        df[v] = pd.to_numeric(df[v])

    # extract relevant variables & info
    df = df[['학교명','학교ID','설립일자','설립형태','소재지지번주소','위도','경도',\
             'class_num_17','student_num_17','teacher_num_17',\
             'class_num_16','student_num_16','teacher_num_16']]
    df = df.rename(columns = {'학교명':'schl_name','학교ID':'schl_id','설립일자':'schl_est',\
                            '설립형태':'schl_type','소재지지번주소':'schl_address',\
                            '위도':'schl_long','경도':'schl_lat'})

    # save
    df.to_csv(clean_path)
