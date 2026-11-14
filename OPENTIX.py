#!/usr/bin/env python
# coding: utf-8

# <a href="https://colab.research.google.com/github/MONNAJAU/practice/blob/main/OPENTIX.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# In[1]:


import requests
from bs4 import BeautifulSoup
import json

# ==========================================
# 第一部分：靜態網頁爬取（取得節目基本資訊）
# ==========================================
event_url = 'https://www.opentix.life/event/2089980031975464960'

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    'Referer': 'https://www.opentix.life/'
}

# 發送 GET 請求並解析 HTML
res_html = requests.get(event_url, headers=headers)
print("網頁狀態碼：", res_html.status_code)

soup = BeautifulSoup(res_html.text, 'html.parser')

# 抓取網頁標題
title_tag = soup.find('title')
if title_tag:
    print("網頁標題：", title_tag.text.strip())

# 抓取 H1 主標題
h1_tag = soup.find('h1')
if h1_tag:
    print("節目名稱：", h1_tag.text.strip())

# 抓取 meta description 節目摘要
meta_desc = soup.find('meta', attrs={'name': 'description'})
if meta_desc:
    print("節目摘要：", meta_desc['content'])

print("-" * 50)

# ==========================================
# 第二部分：動態 API 爬取（取得各票區剩餘座位）
# ==========================================
seats_api_url = 'https://csm.api.opentix.life/events/2066455530077421569/seats'

# 發送 GET 請求並將回傳的字串轉為 JSON 物件
res_api = requests.get(seats_api_url, headers=headers)
print("API 狀態碼：", res_api.status_code)

if res_api.status_code == 200:
    json_data = json.loads(res_api.text)
    seats_list = json_data['result']

    # 建立空字典用來累計各票區剩餘座位（格式：{'票區ID': 數量}）
    remain_counts = {}

    for seat in seats_list:
        section_id = seat['sectionId']
        floor_id = seat['floorId']
        status = seat['status']

        # 組合樓層與票區 ID 當作標籤
        key = f"{floor_id} (區域ID: {section_id})"

        if key not in remain_counts:
            remain_counts[key] = 0

        # status 為 0 代表尚未售出的空位
        if status == 0:
            remain_counts[key] += 1

    # 印出各區統計結果
    print("各票區剩餘座位數統計：")
    for area, count in remain_counts.items():
        print(f"{area}：剩餘 {count} 席")

import csv
import json
import requests
from bs4 import BeautifulSoup

# ==========================================
# 第三部分：將資料寫入 CSV 檔案 (Load)
# ==========================================
csv_file_path = "opentix_remain_seats.csv"

# 開啟檔案準備寫入 (encoding='utf-8-sig' 確保用 Excel 開啟中文不會變亂碼)
with open(csv_file_path, mode="w", newline="", encoding="utf-8-sig") as file:
  writer = csv.writer(file)

  # 1. 寫入 CSV 的標題列 (Header)
  writer.writerow(["票區資訊", "剩餘座位數"])

  # 2. 把 remain_counts 字典裡的資料一筆一筆寫進去
  for area, count in remain_counts.items():
    writer.writerow([area, count])

print(f"資料已經成功存入 {csv_file_path} 囉！")