#!/usr/bin/env python
# coding: utf-8

# In[ ]:


'''
匯入套件
'''
# 操作 browser 的 API
from selenium import webdriver

# 處理逾時例外的工具
from selenium.common.exceptions import TimeoutException

# 面對動態網頁，等待某個元素出現的工具，通常與 exptected_conditions 搭配
from selenium.webdriver.support.ui import WebDriverWait

# 搭配 WebDriverWait 使用，對元素狀態的一種期待條件，若條件發生，則等待結束，往下一行執行
from selenium.webdriver.support import expected_conditions as EC

# 期待元素出現要透過什麼方式指定，通常與 EC、WebDriverWait 一起使用
from selenium.webdriver.common.by import By

# 處理下拉式選單的工具
from selenium.webdriver.support.ui import Select

# 取得系統時間的工具
from datetime import datetime

# 強制等待 (執行期間休息一下)
from time import sleep

# 整理 json 使用的工具
import json,csv

# 執行 command 的時候用的
import os

import requests, json, re

import pandas as pd

import random

import urllib

import urllib.request

from urllib.parse import urljoin


# 啟動瀏覽器工具的選項
options = webdriver.ChromeOptions()
# options.add_argument("--headless")                #不開啟實體瀏覽器背景執行
options.add_argument("--start-maximized")         #最大化視窗
options.add_argument("--incognito")               #開啟無痕模式
options.add_argument("--disable-popup-blocking") #禁用彈出攔截
options.add_argument("--disable-notifications")   #取消通知
options.add_argument('--disable-gpu')
options.add_argument('--disable-plugins')

# 下載路徑 (絕對路徑)(\\是因為參數如果在window下必須要用絕對路徑)
download_path = "C:\\Users\\photo"

# 預設下載路徑
options.add_experimental_option("prefs",{
    "download.default_directory":download_path
})

# 指定 chromedriver 檔案的路徑
executable_path = "./chromedriver.exe"

driver = None


# 匯入檔案

data = pd.read_csv('./photo_list.csv')
listResult = pd.DataFrame(data)


# 存圖位置
local_path = 'photo'
errorData = []
clean_image_urls = []

# WebDriver 初始化
def init():
    global driver 
    driver = webdriver.Chrome(
        options = options,
        executable_path = executable_path
    )
        
# 走訪頁面
def visit():
    driver.get("https://www.google.com.tw/imghp?hl=zh-TW&tab=ri&ogbl");
        
# 輸入關鍵字
def search():
    # 輸入餐廳名稱
    txtInput = driver.find_element(By.CSS_SELECTOR,"input.gLFyf.gsfi")
    txtInput.send_keys(listResult['res_name'][i])
    
    # 定位搜尋按鈕
    input_btn = driver.find_elements(By.CSS_SELECTOR,"span.z1asCe.MZy1Rb svg path")
    
    # 睡
    sleep(random.randint(1, 2))
    
    # 送出搜尋 (There's 2 btn in the elements)
    input_btn[1].submit()

# 分析頁面元素資訊
def parse():
    
    
    for j in range(5):
        # 因為目前來找不到抓取1張高畫質圖片的方法，所以改取得4張圖片連結
        imgClick = driver.find_elements(By.CSS_SELECTOR,"div.bRMDJf.islir img")[j]
        imgClick.click()

        img = driver.find_elements(By.CSS_SELECTOR,"a.eHAdSb img.n3VNCb")[0]
        imgSrc = img.get_attribute('src')

#         print(imgSrc)
        
        # google前兩張照片會存一樣 所j=0不存
        if j != 0:
            filename = listResult['res_name'][i] + '_' + str(j) + '.jpg'
            print(filename)
        else:
            continue
    
# 關閉瀏覽器
def close():
    driver.close()
    driver.quit()
    
#主程式
if __name__ == "__main__":
    for i in range(len(listResult)):
        try:
            init()
            visit()
            search()
            parse()
            close()
            print(f'No.{i+1}/{len(listResult)} finish')
            sleep(1)
        except:
            errorData.append(listResult['res_name'][i])
            continue       

