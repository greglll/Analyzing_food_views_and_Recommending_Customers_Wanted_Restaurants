#!/usr/bin/env python
# coding: utf-8

# In[2]:


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
import json

# 整理 csv 使用的工具
import csv

# 執行 command 的時候用的
import os

import requests, json, re
from bs4 import BeautifulSoup
from pprint import pprint

'''
目的: 爬取EZtable位於台北的餐廳資料並存成餐廳總表(json檔)
餐廳資料包含:"餐廳名稱","Ranking","評論數","餐廳類型","餐廳區域"
'''

# 啟動瀏覽器工具的選項
options = webdriver.ChromeOptions()
# options.add_argument("--headless")                  #不開啟實體瀏覽器背景執行
options.add_argument("--start-maximized")           #最大化視窗
options.add_argument("--incognito")                 #開啟無痕模式
options.add_argument("--disable-popup-blocking")    #禁用彈出攔截
options.add_argument("--disable-notifications")     #取消通知

# 關鍵字
keyword = ""

# 放置爬取的資料
listData = []

# 指定 chromedriver 檔案的路徑
executable_path = "./chromedriver.exe"

# 使用 Chrome 的 Webdriver
driver = webdriver.Chrome(
    options = options,
    executable_path = executable_path
)

# 走訪頁面
def visit():
    driver.get("https://tw.eztable.com/");
    
#輸入關鍵字
def search():
    
    # 按下 餐廳條件篩選
    critab = driver.find_element(By.CSS_SELECTOR, "div#critera-search-tab")
    critab.click()

    # 按下 所有地區   
    allarea = driver.find_element(By.CSS_SELECTOR, "div.sc-hwwEjo.djXUuT")
    allarea.click()    

    # 按下 台北
    tpe = driver.find_elements(By.CSS_SELECTOR, "div.sc-eXEjpC.lgPNjn div.sc-jlyJG.TInyS")[1]
    tpe.click()

    # 按下搜尋
    btnInput = driver.find_element(By.CSS_SELECTOR, "div.sc-gxMtzJ.fjGQvz")
    btnInput.click()

# 滾動頁面
def scroll():
    # 瀏覽器內部的高度
    innerHeightOfWindow = 0
    
    # 當前捲動的量(高度)
    totalOffset = 0
    
    # 在捲動到沒有元素動態產生前，持續捲動
    while totalOffset <= innerHeightOfWindow:
        # 每次移動高度
        totalOffset += 300;
        
        # 捲動的 js code
        js_scroll = '''(
            function (){{
                window.scrollTo({{
                    top:{}, 
                    behavior: 'smooth' 
                }});
            }})();'''.format(totalOffset)
        
        # 執行 js code
        driver.execute_script(js_scroll)
        
        # 強制等待
        sleep(1)
        
        # 透過執行 js 語法來取得捲動後的當前總高度
        innerHeightOfWindow = driver.execute_script(
            'return window.document.documentElement.scrollHeight;'
        );
        
        # 強制等待
        sleep(1)
        
        # 印出捲動距離
        print("innerHeightOfWindow: {}, totalOffset: {}".format(innerHeightOfWindow, totalOffset))
        
def parse():
    count = 0
    
    # 取得主要元素集合
    restaurant_page = driver.find_elements(By.CSS_SELECTOR,"div.row.sc-drKuOJ.cJLQnl")

    # 逐一檢視元素
    for element in restaurant_page:
            # 印出分隔線
            print("="*30)
            
            # 餐廳名字
            name = element.find_element(By.CSS_SELECTOR, 'h4.sc-sdtwF.cuGFHL')
            name = name.text
            print(name)
            
            #餐廳 Ranking
            ranking = element.find_elements(By.CSS_SELECTOR, 'div.sc-kgoBCf.jZzFWu')[0]
            ranking = ranking.text
            ranking = ranking[0:ranking.rfind(' ',1)] # 用index抓出ranking位置
            print(ranking)

            # 評論數
            comment = element.find_elements(By.CSS_SELECTOR, 'div.sc-kgoBCf.jZzFWu')[0]
            comment = comment.text
            comment = comment[comment.rfind('(',1)+1:comment.rfind(')',1)] # 用index抓出comment位置
            print(comment)
            
            # 餐廳類型
            style =  element.find_elements(By.CSS_SELECTOR, 'span.sc-iYUSvU.drMWNT')[0]
            style = style.text
            style = style[8:]
            print(style)
            
            #餐廳區域
            area =  element.find_elements(By.CSS_SELECTOR, 'span.sc-iYUSvU.drMWNT')[0]
            area = area.text
            area = area[2:5]
            print(area)            
            
            # 放資料到 list 當中
            listData.append({
                "餐廳名稱":name,
                "Ranking":ranking,
                "評論數":comment,
                "餐廳類型":style,
                "餐廳區域":area
            })
            
            count += 1
    print('='*30)
    print(f'總餐廳數: {count}')

# 將 list 存成 json
def saveJson():
    fp = open("restaurantList_eztable.json", "w", encoding='utf-8')
    fp.write( json.dumps(listData, ensure_ascii=False) )
    fp.close()


# 關閉瀏覽器
def close():
    driver.quit()

def openJson():
    # 開啟 json 檔案
    fp = open("restaurantList_eztable.json", "r", encoding='utf-8')
    
    #取得 json 字串
    strJson = fp.read()
    
    # 關閉檔案
    fp.close()
    
    # 將 json 轉成 list (裡面是 dict 集合)
    listResult = json.loads(strJson)
    
#主程式
if __name__ == "__main__":
    visit()
    search()
    scroll()
    parse()
    saveJson()
    close()

