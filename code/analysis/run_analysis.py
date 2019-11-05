'''
Created on Nov 4th, 2019

@author: sookyojeong

This script runs codes to clean air pollution & school data.

'''
# import packages
import argparse

from descriptive import main as descriptive
from variables import main as variables
from ols import main as ols

import os
import pandas as pd
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('script',nargs='?',type=str,default='all', help='Script number to run, -all- for all scripts')
args = parser.parse_args()

# common paths
analysis_clean = '../../data/clean/analysis_clean.csv'
tables_raw = '../../output/tables_raw.xlsx'

if args.script=='all' or args.script=='variables':
    variables(input_path = '../../data/clean/dataClean_bymonth.csv',
                output_path = analysis_clean)
    
if args.script=='all' or args.script == 'descriptive':
    descriptive(input_path = analysis_clean)
    
if args.script=='all' or args.script=='ols':
    ols(input_path = analysis_clean)
 
