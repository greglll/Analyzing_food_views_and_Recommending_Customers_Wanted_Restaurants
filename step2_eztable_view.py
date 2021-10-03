#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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
目的: 爬取EZtable餐廳總表(json檔)中各餐廳的評論集
評論集包含:"餐廳名稱","地址","機器分析評論","評論者","評論日期","評論rank","評論"
'''

# 啟動瀏覽器工具的選項
options = webdriver.ChromeOptions()
# options.add_argument("--headless")                  #不開啟實體瀏覽器背景執行
options.add_argument("--start-maximized")           #最大化視窗
options.add_argument("--incognito")                 #開啟無痕模式
options.add_argument("--disable-popup-blocking")    #禁用彈出攔截
options.add_argument("--disable-notifications")     #取消通知

# 指定 chromedriver 檔案的路徑
executable_path = "./chromedriver.exe"

# 使用 Chrome 的 Webdriver
driver = webdriver.Chrome(
    options = options,
    executable_path = executable_path
)

# 放置爬取的資料
listComment = []
errorRestaurant = []

# 走訪頁面
def visit():
    
    # 紀錄有評論的餐廳數
    restaurant_with_comment = 0
    
    # 開啟 json 檔案
    fp = open("restaurantList_eztable.json", "r", encoding='utf-8')

    #取得 json 字串
    strJson = fp.read()

    # 關閉檔案
    fp.close()

    # 將 json 轉成 list (裡面是 dict 集合)
    listResult = json.loads(strJson)
    print(len(listResult))
    
    # 去那個網站
    driver.get("https://tw.eztable.com/");
    
    # 調整起始店家

def parse():
    for i in range(len(listResult)):
        
        if listResult[i]['評論數'] == "0":
            pass
        
        else:
            try:
                # 評論數+1
                restaurant_with_comment += 1

                # 以餐廳名稱搜尋
                commentClick = driver.find_elements(By.CSS_SELECTOR, "div.sc-TOsTZ.hLHrTT")[0]
                commentClick.click()
                input = driver.find_element(By.CSS_SELECTOR, "input#search-input")
                input.send_keys(listResult[i]['餐廳名稱'])
                # 按下搜尋
                btnInput = driver.find_element(By.CSS_SELECTOR, "div.sc-gxMtzJ.fjGQvz")
                btnInput.click()

                # 休息
                sleep(5)

                # 點進餐廳頁面
                gotorestaurant = driver.find_elements(By.CSS_SELECTOR, "h4.sc-sdtwF.cuGFHL")[0]
                gotorestaurant.click()    

                # 休息
                sleep(5)
                 
                # 從此網址開始
                driver.get(driver.current_url)
                
                # 從"資訊"分頁抓取餐廳地址
                address = driver.find_elements(By.CSS_SELECTOR,"div.sc-iGrrsa.dCSTKH p.sc-hMqMXs.lmjHFQ")[0]
                address = address.text

                # 按下評論分頁
                commentClick = driver.find_elements(By.CSS_SELECTOR, "div.sc-gisBJw.dJhIVU")[1]
                commentClick .click()

                # 滾動頁面

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

                    # 為了實驗功能，捲動超過一定的距離，就結束程式
            #         if totalOffset >= 1000:
            #             break

                # 抓取評論
                count = 0 

                # 取得主要元素集合
                comment_page = driver.find_elements(By.CSS_SELECTOR,"div.sc-yZwTr.TvXeg")

                # 官方宣稱論數
                commorg =  driver.find_elements(By.CSS_SELECTOR, 'span.sc-iAyFgw.ecZwUw')[0]
                commorg = commorg.text
                commorg = commorg[0:commorg.rfind(' ',1)]
                listComment.append({"官方宣稱評論數": commorg})

                # 逐一檢視元素
                for element in comment_page:
                        # 印出分隔線
                        print("="*30)

                        print(listResult[i]['餐廳名稱'])

                        # 機器分析評論
                        commbot = element.find_element(By.CSS_SELECTOR, 'h4.sc-jKJlTe.kUzHiO')
                        commbot = commbot.text
                        print(commbot)

                        #評論者
                        commenter = element.find_elements(By.CSS_SELECTOR, 'span.sc-bbkauy.gjTxnp')[0]
                        commenter = commenter.text
                        commenter = commenter[0:commenter.rfind(' /',1)] # 用index抓出ranking位置
                        print(commenter)

                        # 評論日期
                        commdate = element.find_elements(By.CSS_SELECTOR, 'span.sc-bbkauy.gjTxnp')[0]
                        commdate = commdate.text
                        commdate = commdate[commdate.rfind('/ ',1)+2:] # 用index抓出comment位置
                        print(commdate)

                        # 評論rank
                        commrank =  element.find_elements(By.CSS_SELECTOR, 'img.sc-iuDHTM.imDQUC')[0]
                        commrank = commrank.get_attribute('src')
                        commrank = commrank
                        commrank = commrank[commrank.rfind('_',1)+1:commrank.rfind('-26811-4.svg',1)]
                        print(commrank)

                        # 評論
                        comment = element.find_elements(By.CSS_SELECTOR, 'span.sc-kkGfuU.daQGNB')[0]
                        comment = comment.text
                        print(comment)            

                        # 放資料到 list 當中
                        listComment.append({
                            "餐廳名稱":listResult[i]['餐廳名稱'],
                            "地址":address,
                            "機器分析評論":commbot,
                            "評論者":commenter,
                            "評論日期":commdate,
                            "評論rank":commrank,
                            "評論":comment
                        })

                        count += 1

                # 餐廳總結
                print('='*30)
                print(listResult[i]['餐廳名稱'])
                print(f'官方宣稱評論數: {commorg}')
                print(f'實際評論數: {count}')
                print(f'有評論/餐廳總數 : {restaurant_with_comment}/{i+1}')

                #  回到上一頁
                driver.back()
            except:
                errorRestaurant.append(i)


        sleep(5)
    print('='*30)

    
def close():
    # 關閉瀏覽器
    driver.quit()
    
    
# 將 list 存成 json
def saveJson():
    fp = open("eztable_view.json", "w", encoding='utf-8')
    fp.write( json.dumps(listComment, ensure_ascii=False) )
    fp.close()


#主程式
if __name__ == "__main__":
    visit()
    parse()
    close()
    saveJson()

