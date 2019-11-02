 '''
Created on Apr 28, 2019

@author: sookyojeong

This code will read in list of all high schools in Korea, read in the number of 
students, classes and teachers from the website schoolinfo.gov.kr, and match with
the main school data (provided by edss) to 
'''
# import packages
import os
import pandas as pd
import numpy as np
pd.set_option('display.max_columns',999) 
import selenium.webdriver as webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

def split(dfm, chunk_size):
    indices = index_marks(dfm.shape[0], chunk_size)
    return np.split(dfm, indices)

def index_marks(nrows, chunk_size):
    return range(1 * chunk_size, (nrows // chunk_size + 1) * chunk_size, chunk_size)

def get_results(search_term):
    
    # print some identifying info for debugging purposes
    print("\n",search_term)
    
    # initialize return variables
    est = type = ''
    print('1')
    
    # initialize web browser
    browser = webdriver.Chrome(chrome_options=options, executable_path=chromedriver)
    browser.get(url)
    
    # search for the specific school
    search_box = browser.find_element_by_id("SEARCH_KEYWORD")
    search_box.send_keys(search_term)
    search_box.submit()
    print('2')
    
    # sometimes, there  will be no such school.
    # sometimes, there will be more than one such school. In that case, exit the function and handle manually
    try:
        browser.find_element_by_xpath("//a[text()[contains(.,'폐교')]]")
        print('pass: school is closed')
        browser.quit()
        return est, type
    except:
        pass
    
    nschl=np.nan
    nschl = len(browser.find_elements_by_xpath("//*[@id='SchoolListWrap']/article"))
    print('3')
    list = []
    if (nschl==0):
        print('pass: no such school exists')
        return est, type
    elif (nschl>1):
        for i in range(1,nschl+1):
            if (browser.find_element_by_xpath("//*[@id='SchoolListWrap']/article["+str(i)+"]//a").text == search_term):
                list.append(i)
        if (len(list)>1):
            print('pass: more than one such school')
            browser.quit()
            return est, type
        else:
            browser.find_element_by_link_text(search_term).click()
    else:
        browser.find_element_by_link_text(search_term).click()
    print('4')
    
    # time out exception
    try:
        WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.XPATH, "//span[text()[contains(.,'개교기념일')]]")))
    except:
        print('too much time passed')
        browser.quit()
        return est, type

    # save establishment date
    est = browser.find_element_by_xpath("//*[@id='Contents']/div/article/div/ul/li[6]").text
    est = est[6:]
    
    # save school type
    type = browser.find_element_by_xpath("//*[@id='Contents']/div/article/div/ul/li[2]").text
    type = type[5:]
    
    # print results
    print('설립일:',est, ', 구분:',type)
    
    # return values
    browser.quit()
    return est, type
    
def main(raw_path,driver,clean_path):
    # specify chrome options
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--headless")
    options.add_argument('--ignore-ssl-errors')

    # set up chrome driver
    chromedriver = driver
    os.environ["webdriver.chrome.driver"]=chromedriver
    url = 'https://www.schoolinfo.go.kr/'

    # initialize counter
    delay = 5 # seconds
    startfile = 31
    endfile = 0
    # function for getting student numbers, class nums, and teacher numbers
    # input: search_term: name of high school
    # output:
    # initiate browser
      
    # set directory
    root = "/Users/sookyojeong/Dropbox/pm25/data"
    df = pd.read_excel(raw_path,encoding='cp949')
    df = df[df['학교급구분'] == '고등학교'] # restrict to high schools

    # handle name change
    df = df.replace(to_replace='부산에너지과학고등학교', value='서부산공업고등학교', regex=True)
    df = df.replace(to_replace='영락유헬스고등학교', value='영락의료과학고등학교', regex=True)
    df = df.replace(to_replace='경북관광고등학교', value='경북조리과학고등학교', regex=True)
    df = df.replace(to_replace='수원전산여자고등학교', value='한봄고등학교', regex=True)
    df = df.replace(to_replace='군자디지털과학고', value='군자디지털과학고등학교', regex=True)

    # reset index and sort
    df = df.sort_values(by=['학교ID'])
    df = df.reset_index()

    # divvy up the dataset and append later
    chunks = split(df, 100)
    endfile = len(chunks)
    print(endfile)
    counter = 0
    for c in chunks:
        if (counter >= startfile)&(counter<=endfile):
            c['est'], c['type'] = zip(*c.apply(lambda x: get_results(x['학교명']), axis=1))
            c.to_csv(os.path.join(clean_path,'highschools2_'+str(counter)+'.csv'), encoding='utf-8', index=False)
        counter = counter+1
