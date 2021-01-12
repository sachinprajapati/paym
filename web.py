from bhartipay import StartProccess
import chromedriver_autoinstaller
from selenium import webdriver
import pandas as pd
from datetime import datetime
import time, os

url = 'https://dcrgpay.com/payment/'
# url = 'https://merchant.bhartipay.com/formpay/i/97099'
file = pd.read_csv("data.csv")
file['date'] = pd.to_datetime(file.date)

chromedriver_autoinstaller.install()
driver = webdriver.Chrome()

for index, row in file.iterrows():
    n_trans = 2
    retry = 2
    failed = 0
    success_status = 0
    while n_trans != success_status:
        if failed == 3:
            break
        driver.get(url)
        sp = StartProccess(driver, row.to_dict())
        if not sp.Completed():
            failed += 1
            print("failed")
            continue
        else:
            if sp.getStatus():
                success_status += 1
                print("success")
            else:
                retry -= 1
                print("not success")
        if retry == 0:
            if success_status > 0:
                retry = n_trans - success_status
            else:
                break
