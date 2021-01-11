import time, glob, csv, sys, os
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import pandas as pd
import numpy as np
from pyexcel.cookbook import merge_all_to_a_book
import glob
from numpy import nan as Nan
from shutil import copyfile

# Globals
url = 'https://dcrgpay.com/payment/'
username = ['GCKC_ROOPVAS', 'GCKC_BHARATPUR']
password = 'PASSWORD'
load_wait_time = 20
download_retries = 3
download_dir = '/tmp/'
upload_dir='/home/sachin'
dir_path = os.path.dirname(os.path.realpath(__file__))

def login(driver, user):
    elem = driver.find_element_by_name('user_name')
    #elem.send_keys(username)
    elem.send_keys(user)
    elem = driver.find_element_by_name('password')
    elem.send_keys(password)
    elem = driver.find_element_by_id('btn-login')
    elem.click()
    time.sleep(load_wait_time)
    print ("logged In")
    # check if we are logged in
    if ('Registered Devices' not in driver.page_source):
        raise Exception('Cannot login, please try again')

def get_device_table_elements(driver):
    device_list_table = driver.find_element_by_xpath('//*[@id="device-list-table"]/tbody')
    html = device_list_table.get_attribute('outerHTML')
    device_list_elements = device_list_table.find_elements_by_tag_name('tr')
    return(device_list_elements)

def change_name(i, user):
    list_of_files = glob.glob(download_dir+'*.xls') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    file_new_name = user+'_'+str(i+1)+'.xls'
    try:
        os.remove(download_dir+file_new_name)
    except OSError:
        pass
    new_name = os.rename(latest_file, download_dir+file_new_name)
    print (file_new_name)
    data=pd.read_html(download_dir+file_new_name, header=None)
    df = pd.DataFrame(data[1])
    try:
        df['Process Value'] = df['Process Value'].str.strip('meter')
    except :
        pass
    try:
        df['Flow Value'] = df['Flow Value'].str.strip('m3')
    except:
        pass
    if df.empty:
        df = df.append({'Channel': '', 'Time': '', 'Flow Value': '', 'Process Value': '', 'Battery Level': ''}, ignore_index=True)
        
    df = df.iloc[:1]
    print (df)
    df['device'] = file_new_name
    df.to_csv('/tmp/xls_to_csv.csv',header=False,index=False,mode='a')

try:
    
    try:
        os.remove('/tmp/xls_to_csv.csv')
    except OSError:
        pass

    with open('/tmp/xls_to_csv.csv', "w+") as outcsv:
            writer = csv.writer(outcsv)
            writer.writerow(["Channel","Time","Flow Value","Process Value","Battery Level","device"])
            
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", download_dir)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.ms-excel")

    options = Options()
    #options.add_argument("--headless")

    binary = FirefoxBinary('/usr/bin/firefox')
    driver = webdriver.Firefox(firefox_binary=binary, executable_path=dir_path+'/geckodriver', options=options, firefox_profile=profile)
    #driver = webdriver.Firefox()
    for user in username:
        print (user)
        driver.get(url)
        login(driver,user)

        device_list_elements = get_device_table_elements(driver)
        device_count = len(device_list_elements)

        for i in range(device_count):
            time.sleep(load_wait_time)
            print ("Device id:",(i+1))
            elem = driver.find_element_by_xpath('//p[text()=' +str(i+1)+']')
            elem.click()
            time.sleep(10)

            retries = download_retries
            for retry in range(retries):
                if ('Export to Excel' in driver.page_source):
                    download_button = driver.find_element_by_link_text('Export to Excel')
                    download_button.click()
                    #time.sleep(load_wait_time)
                    print ('file downloaded')
                    change_name(i, user)
                    device_page_link = driver.find_element_by_link_text('Devices')
                    device_page_link.click()
                    print('Go to devices page')
                    time.sleep(load_wait_time)
                    break
                else:
                    print(str(i), ':',
                          'retry', '[#', retry, ']',
                          'Error: cannot find download Excel button')
                    time.sleep(load_wait_time)

        print("Download all files in /tmp directory")
        #device_page_link = driver.find_element_by_link_text('Devices')
        #device_page_link.click()
        #time.sleep(load_wait_time)

    # XXX
        #device_list_elements = get_device_table_elements(driver) # refresh device list

    print ("excel file converted")
    copyfile(download_dir+"xls_to_csv.csv", download_dir+"x_to_c.csv")
    merge_all_to_a_book(glob.glob(download_dir+"x_to_c.csv"), upload_dir+"telecon.xlsx")
    print("copy telecon to reports all completed")

except Exception as err:
    raise err

else:
    driver.close()
