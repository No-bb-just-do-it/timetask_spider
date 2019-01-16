import redis
import requests
import logging
import time
import pymysql
from datetime import datetime, date, timedelta


class MiitPipeline(object):
    def __init__(self):
        # 连接数据库
        self.conn = None
        # 游标
        self.cur = None
        # 今日日期
        self.today = str(date.today())
        # 昨日日期
        self.yesterday = str(date.today() + timedelta(days = -1))

    # 打开爬虫时调用，只调用一次
    def open_spider(self, spider):
        self.conn = pymysql.connect(host='47.106.13.62',
                                    user='root',
                                    password='jiayou875',
                                    database='zbytb4',
                                    port=3306,
                                    charset='utf8')
        self.cur = self.conn.cursor()

    def process_item(self, item, spider):
        if 'addr_id' and 'title' and 'url' and 'intro' in item:
            if item['web_time'] == self.today or item['web_time'] == self.yesterday:
                item['web_time'] = int(time.mktime(time.strptime(item['web_time'], "%Y-%m-%d")))
                try:
                    # 正式上传到服务器
                    sql = "INSERT INTO ztb_info_25 (itemid,catid,title,style,addtime,adddate,areaid,status,linkurl,content) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (
                    'NULL', item['type_id'], item['title'], item['source_name'], item['time'], item['web_time'],
                    item['addr_id'], 3, item['url'], pymysql.escape_string(item['intro']))

                    # 单机测试
                    # sql = "INSERT INTO ztb_info_25 (catid,title,style,addtime,adddate,areaid,status,linkurl,content) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (
                    #     item['type_id'], item['title'], item['source_name'], item['time'], item['web_time'],
                    # item['addr_id'], 3, item['url'], pymysql.escape_string(item['intro']))

                    self.cur.execute(sql)
                    # self.conn.commit()
                    self.cur.fetchall()

                except Exception as e:
                    print(item['url'])
                    print(item['title'])
                    print('上传服务器出错')
                    print(e)
                    pass
                # else:
                #     print('ok')

        elif 'addr_id' not in item:
            print(item['url'])
            print(item['title'])
            print('addr_id为空')
        elif 'title' not in item:
            print(item['url'])
            print(item['title'])
            print('title为空')
        elif 'url' not in item:
            print(item['url'])
            print(item['title'])
            print('url为空')
        elif 'inrto' not in item:
            print(item['url'])
            print(item['title'])

    def close_spider(self, spider):
        self.conn.close()
