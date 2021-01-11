from tkinter import *
from tkinter.ttk import *

from tkinter.filedialog import askopenfile 

from bhartipay import StartProccess
import chromedriver_autoinstaller
from selenium import webdriver
import pandas as pd
from datetime import datetime
import time, os
import re

url = 'https://dcrgpay.com/payment/'
# url = 'https://merchant.bhartipay.com/formpay/i/97099'

root = Tk() 
root.geometry('200x100') 

def open_file(): 
    file = askopenfile(mode ='r', filetypes =[("Excel files", ".xlsx .xls")]) 
    if file is not None: 
        content = pd.read_excel(file, engine="openpyxl")
        print(content) 

btn = Button(root, text ='Open', command = lambda:open_file()) 
btn.pack(side = TOP, pady = 10) 

mainloop() 
