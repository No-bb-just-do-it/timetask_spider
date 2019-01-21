import redis
import requests
import logging
import time
import pymysql
from datetime import datetime, date, timedelta
import time

class ChinaTelecomPipeline(object):
    def __init__(self):
        # 连接数据库
        self.conn = None
        # 游标
        self.cur = None
        # 获取当前日期
        self.today = str(date.today())
#
#     # 打开爬虫时调用，只调用一次
#     def open_spider(self, spider):
#         self.conn = pymysql.connect(host='47.106.13.62',
#                                     user='root',
#                                     password='jiayou875',
#                                     database='zbytb4',
#                                     port=3306,
#                                     charset='utf8')
#         self.cur = self.conn.cursor()
#
    def process_item(self, item, spider):
        # if 'addr_id' and 'title' and 'url' and 'intro' in item and self.today == item['web_time']:
        if 'addr_id' and 'title' and 'url' and 'intro' in item:
            print('ok')
#             try:
#                 sql = "INSERT INTO ztb_info_25 (itemid,catid,title,style,addtime,adddate,areaid,status,linkurl,content) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (
#                 'NULL', item['type_id'], item['title'], item['source_name'], item['time'], item['web_time'],
#                 item['addr_id'], 3, item['url'], pymysql.escape_string(item['intro']))
#                 self.cur.execute(sql)
#                 self.cur.fetchall()
#             except Exception as e:
#                 print(e)
#                 pass
#             else:
#                 print('ok')
#
#     def close_spider(self, spider):
#         self.conn.close()