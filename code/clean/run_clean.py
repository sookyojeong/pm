'''
Created on Nov 2nd, 2019

@author: sookyojeong

This script runs codes to clean air pollution & school data.

'''
# import packages
import argparse

from clean_chemicals_bymonth import main as chemical
from clean_sites import main as weather_sites
from clean_weather_bymonth import main as weather
from clean_schools4 import main as schools
from school_crosswalk2 import main as crosswalk
from clean_schools2 import main as schools_scrape
from clean_highschools_downloaded import main as schools_scrape_clean
from clean_schools3_bymonth import main as combine
from distance_schools import main as distance

import os
import pandas as pd
import numpy as np

pd.set_option('display.max_columns',999) 

parser = argparse.ArgumentParser()
parser.add_argument('script',nargs='?',type=str,default='all', help='Script number to run, -all- for all scripts')
args = parser.parse_args()

if args.script=='all' or args.script == 'chemical':
    weather_sites(raw_path='../../data/raw',
    clean_path = '../../data/clean/siteClean.csv')
    chemical(raw_path = '../../data/raw',
    clean_path = '../../data/clean/monitorClean_bymonth.csv')

if args.script=='all' or args.script == 'weather':
    weather(raw_path='../../data/raw/weather_historical.csv',
    site_path = '../../data/raw/weater_site.csv',
    clean_path='../../data/clean/cleanWeather_bymonth.csv')
    
if args.script=='all' or args.script=='scrape':
    schools_scrape(raw_path='../../data/raw/schools.xls',
    driver = './chromedriver',
    clean_path='../../data/clean/highschool_scraped')
    schools_scrape_clean(raw_path='../../data/clean/highschool_scraped',
    clean_path = '../../data/clean/highschlinfo_clean.csv')
    
if args.script=='all' or args.script=='schools':
    crosswalk(input_x1_schools = '../../data/clean/highschool_nums_final.csv',
    input_x1_schools_type ='../../data/clean/highschool_types.csv',
    input_x2_schools_basic = '../../data/raw/edss/schools_basic.csv',
    input_x2_schools_vars = '../../data/raw/edss/schools_vars.csv',
    clean_path = '../../data/clean/highschool_crosswalk3.csv')
    schools(input_basic='../../data/raw/edss/schools_basic.csv',
    input_vars='../../data/raw/edss/schools_vars.csv',
    input_test='../../data/raw/edss/exams/scores/highschool_exams.xlsx',
    input_xwalk = '../../data/clean/highschool_crosswalk3.csv',
    input_geo = '../../data/raw/schools.xls',
    clean_path='../../data/clean/schoolClean.csv')
    
if args.script=='all' or args.script=='combine':
    distance(input_schools = '../../data/clean/schoolClean.csv',
    input_chem_sites = '../../data/clean/siteClean_manualgeocoded.xlsx',
    input_w_sites = '../../data/clean/weather_site_merged.csv',
    input_regions = '../../data/clean/hhinc.csv',
    clean_path = '../../data/clean/schoolClean_wdist.csv')
    combine(input_schools = '../../data/clean/schoolClean.csv',
    input_schools_dist = '../../data/clean/schoolClean_wdist.csv',
    input_college = '../../data/clean/college_entrance.csv',
    input_chemical = '../../data/clean/monitorClean_bymonth.csv',
    input_weather = '../../data/clean/cleanWeather_bymonth.csv',
    input_region = '../../data/clean/hhinc.csv',
    input_region_demo = '../../data/clean/hhinc_demo.csv',
    clean_path='../../data/clean/dataClean_bymonth.csv')
    
