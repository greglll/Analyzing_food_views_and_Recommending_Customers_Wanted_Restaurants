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

# 啟動瀏覽器工具的選項
options = webdriver.ChromeOptions()
options.add_argument("--headless")                #不開啟實體瀏覽器背景執行
options.add_argument("--start-maximized")         #最大化視窗
options.add_argument("--incognito")               #開啟無痕模式
options.add_argument("--disable-popup-blocking") #禁用彈出攔截
options.add_argument("--disable-notifications")   #取消通知
options.add_argument("blink-settings=imagesEnabled=false") # 不載入圖片
options.add_argument('--disable-gpu')
options.add_argument('--disable-plugins')

# 建立儲存圖片或檔案的資料夾，不存在就新增
folderPath = "restaurants"
if not os.path.exists(folderPath):
    os.makedirs(folderPath)
    
# 下載路徑 (絕對路徑)(\\是因為參數如果在window下必須要用絕對路徑)
download_path = "C:\\Users\\restaurants"

# 預設下載路徑
options.add_experimental_option("prefs",{
    "download.default_directory":download_path
})

# 指定 chromedriver 檔案的路徑
executable_path = "./chromedriver.exe"

driver = None

# 將餐廳檔讀入，將餐廳名稱抓進 list
df = pd.read_csv('google_restaurant_list.csv')
rest_list = df['餐廳名稱'].to_list()
print(len(rest_list))


# WebDriver 初始化
def init():
    global driver 
    driver = webdriver.Chrome(
        options = options,
        executable_path = executable_path
    )

# 走訪頁面
def visit():
    driver.get("https://www.google.com.tw");

# 輸入關鍵字
def search():
    # 輸入餐廳名稱
    txtInput = driver.find_element(By.CSS_SELECTOR,"input.gLFyf.gsfi")
    txtInput.send_keys(rest_list[i])
    
    # 定位搜尋按鈕
    input_btn = driver.find_elements(By.CSS_SELECTOR,"div.lJ9FBc input.gNO89b")
    
    # 睡
    sleep(random.randint(3, 5))
    
    # 送出搜尋 (There's 2 btn in the elements)
    input_btn[1].submit()  
    
    # 點選地圖，並定位 MAP 元素
    mapInput = driver.find_elements(By.CSS_SELECTOR,"div.hdtb-mitem a")
    mapInput[0].click()
    driver.implicitly_wait(10)
    
    # 點進評論
    review_link = driver.find_elements(By.CSS_SELECTOR,"button.widget-pane-link")
    if len(review_link) < 1:
        multi_result = driver.find_elements(By.CSS_SELECTOR,"a.a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd")
        multi_result[0].click()
        review_link = driver.find_elements(By.CSS_SELECTOR,"button.widget-pane-link")
        
    # 睡
    sleep(0.5)
    
    # 送出搜尋
    review_link[0].click()
    
    # 睡
    sleep(2)
    
    # 將評論以最新排序，定位最新排序按鈕
    order_menu = driver.find_element(By.CSS_SELECTOR,"button[aria-label='排序評論']")
    order_menu.click()
    btn_newest = driver.find_element(By.CSS_SELECTOR, "li[data-index='1']")
    btn_newest.click()    
    

# 分析頁面元素資訊
def parse():
    global rvwData
    rvwData = []  # For comments only
    
    rvw = driver.find_element(By.CSS_SELECTOR,"div.gm2-caption")
    driver.implicitly_wait(5)
    
    rest_sumrvw = rvw.text
    rest_sumrvw = re.split(" ",rest_sumrvw)[0]
    rest_sumrvw = rest_sumrvw.replace(",","")
    print(rest_sumrvw)
    
    # 可滾動目標
    scrolling_blk = driver.find_element(By.CSS_SELECTOR,"div.section-layout.section-scrollbox.cYB2Ge-oHo7ed.cYB2Ge-ti6hGc")

    # 頁面可見的評論數
    visible_rvw = driver.find_elements(By.CSS_SELECTOR,"div.ODSEW-ShBeI.NIyLF-haAclf.gm2-body-2") 

    for s in range(10000):
        
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrolling_blk)
        visible_rvw = driver.find_elements(By.CSS_SELECTOR,"div.ODSEW-ShBeI.NIyLF-haAclf.gm2-body-2")
#         if len(visible_rvw) == int(rest_sumrvw):
        if len(visible_rvw) > 200:
            break
        else:
            if len(visible_rvw) == int(rest_sumrvw):
                break
        print(len(visible_rvw))        
        sleep(1)
        
    rvw_order = 0
    for o in visible_rvw:

        # 評論者 
        user_blk = o.find_element(By.CSS_SELECTOR,"div.ODSEW-ShBeI-title span")
        user = user_blk.text                  

        # 評分星等
        star_blk = o.find_element(By.CSS_SELECTOR,"span[role='img']").get_attribute('aria-label')
        starNum = re.split("：| ", star_blk)[1]           

        # 留言編號
        rvw_order += 1
        
        # 留言內容
        extra_button = o.find_elements(By.CSS_SELECTOR,"button.ODSEW-KoToPc-ShBeI.gXqMYb-hSRGPd")
        if len(extra_button) > 0:
            extra_button[0].click()
        
        rvw_msg = o.find_element(By.CSS_SELECTOR,"div.ODSEW-ShBeI-ShBeI-content")
        rvw_text = rvw_msg.text
        if len(rvw_text)==0:
            rvw_text = "NA"


        # 留言時間
        time_blk = o.find_element(By.CSS_SELECTOR,"span.ODSEW-ShBeI-RgZmSc-date")
        rvw_time = time_blk.text     

        # 放資料到 list 當中
        rvwData.append({
            "餐廳名稱": rest_list[i],
            "留言排序":rvw_order,
            "評論數": rest_sumrvw,
            "留言ID": user,
            "評論星數": starNum,
            "留言內容": rvw_text,
            "留言時間": rvw_time
        })
    
        print(rvw_order)

# 寫入 CSV
def csv_writer():

    filename = f'restaurants/reviews_{i+1}.csv'

    with open(filename,'w', newline='',encoding="utf-8") as csvfile:
        # 定義欄位
        rvwNames = ["餐廳名稱", "留言排序", "評論數", "留言ID", "評論星數", "留言內容","留言時間"]                    

        # 將 dict 寫入 CSV file
        writer = csv.DictWriter(csvfile, fieldnames=rvwNames)

        # 寫入第一列的欄位名稱
        writer.writeheader()

        # 寫入內容
        for item in rvwData:
            writer.writerow(item);
    
    del globals()['rvwData']

            
# 關閉瀏覽器
def close():
    driver.close()
    driver.quit()
    
    
    
#主程式
if __name__ == "__main__":
    for i in range(1933, 2000):
        print(f'No.{i+1} start')
        init()
        visit()
        try:
            search()
        except:
            continue
        
        try:
            parse()
        except:
            continue
        
        try:
            csv_writer()
        except:
            continue
        close()
        print(f'No.{i+1} finish')
        sleep(random.randint(3, 5))

