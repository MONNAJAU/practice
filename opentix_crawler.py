import requests
import json
import time
from datetime import datetime
import pymysql

# ==========================================
# 1. 資料庫設定與寫入函式
# ==========================================
db_config = {
    'host': 'localhost',
    'user': 'root',          # 請換成你的 MySQL 帳號
    'password': 'password',  # 請換成你的 MySQL 密碼
    'database': 'opentix_db',
    'charset': 'utf8mb4'
}

def save_to_mysql(records):
    if not records:
        return
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    sql = """
        INSERT INTO opentix_tickets (EVENT_NAME, EVENT_TIME, REMAIN_SEATS, PRICE)
        VALUES (%s, %s, %s, %s)
    """
    try:
        cursor.executemany(sql, records)
        conn.commit()
        print(f"成功寫入 {len(records)} 筆資料到 MySQL！")
    except Exception as e:
        conn.rollback()
        print("資料庫寫入失敗：", e)
    finally:
        cursor.close()
        conn.close()

# ==========================================
# 2. 爬蟲設定與主程式
# ==========================================
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    'Referer': 'https://www.opentix.life/'
}

# 設定要爬取的頁數範圍（測試階段先抓第 1 頁，確認無誤可改為 while 迴圈抓全部）
max_pages = 1
all_records = []

for page in range(1, max_pages + 1):
    list_url = f'https://csm.api.opentix.life/programs?page={page}&rowCount=10'
    res_list = requests.get(list_url, headers=headers)
    
    if res_list.status_code != 200:
        print(f"第 {page} 頁列表請求失敗")
        break
        
    list_data = json.loads(res_list.text)
    programs = list_data.get('result', {}).get('data', [])
    
    if not programs:
        break
        
    for prog in programs:
        prog_id = prog['id']
        prog_name = prog['name']
        print(f"正在爬取節目：{prog_name} (ID: {prog_id})")
        
        # 請求單檔節目詳細資料 API
        detail_url = f'https://csm.api.opentix.life/programs/{prog_id}'
        res_detail = requests.get(detail_url, headers=headers)
        
        if res_detail.status_code == 200:
            detail_data = json.loads(res_detail.text)['result']
            event_venues = detail_data.get('eventVenues', [])
            
            for venue in event_venues:
                events = venue.get('events', [])
                for event in events:
                    # 將 Unix 時間戳記轉換為可讀的日期時間字串
                    start_ts = event.get('startDateTime')
                    event_time_str = datetime.fromtimestamp(start_ts).strftime('%Y-%m-%d %H:%M:%S') if start_ts else '未定'
                    
                    # 取得各票區票價與剩餘席次
                    group_sections = event.get('groupSections', {})
                    for group_key, sections in group_sections.items():
                        for sec in sections:
                            price = sec.get('price', 0)
                            remain_seats = sec.get('quantity', {}).get('remainingQuantity', 0)
                            
                            # 整理成 tuple 準備批次寫入資料庫
                            all_records.append((prog_name, event_time_str, remain_seats, price))
                            
        # 禮貌性暫停 0.5 秒，避免請求過快
        time.sleep(0.5)

# 印出前 5 筆抓到的資料預覽
print("-" * 50)
print(f"總共整理出 {len(all_records)} 筆票區資料，前 5 筆預覽：")
for r in all_records[:5]:
    print(r)

# 寫入 MySQL 資料庫
save_to_mysql(all_records)
