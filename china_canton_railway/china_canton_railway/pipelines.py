import redis
import requests
import logging
import time
import pymysql
from datetime import datetime, date, timedelta


class UniversalPipeline(object):
    def __init__(self):
        # 连接数据库
        self.conn = None
        # 游标
        self.cur = None
        # # 今日日期
        # self.today = str(date.today())
        # # 昨日日期
        # self.yesterday = str(date.today() + timedelta(days = -1))

    # 打开爬虫时调用，只调用一次
    def open_spider(self, spider):
        self.conn = pymysql.connect(host='47.106.13.62',
                                    user='root',
                                    password='jiayou875',
                                    database='test_demo',
                                    port=3306,
                                    charset='utf8')
        self.cur = self.conn.cursor()

    def process_item(self, item, spider):
        # if item['web_time'] == self.today or item['web_time'] == self.yesterday:
        try:
            if item['addr_id'] != '' and item['title'] != '' and item['url'] != '' and item['intro'] != '' and item['web_time'] != '' :
                item['web_time'] = int(time.mktime(time.strptime(item['web_time'], "%Y-%m-%d")))
            #     # 正式上传到服务器
            #     sql = "INSERT INTO ztb_info_25 (catid,title,style,addtime,adddate,areaid,status,linkurl,content) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (
            #     item['type_id'], item['title'], item['source_name'], item['time'], item['web_time'],
            #     item['addr_id'], 3, item['url'], pymysql.escape_string(item['intro']))

                # 单机测试
                sql = "INSERT INTO demo (catid,title,style,addtime,adddate,areaid,status,linkurl,content) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (
                    item['type_id'], item['title'], item['source_name'], item['time'], item['web_time'],
                item['addr_id'], 3, item['url'], pymysql.escape_string(item['intro']))

                self.cur.execute(sql)
                self.cur.fetchall()
                self.conn.commit()

            else:
                try:
                    item['web_time'] = int(time.mktime(time.strptime(item['web_time'], "%Y-%m-%d")))
                except:
                    pass

                sql = "INSERT INTO ztb_error_infos (catid,title,style,addtime,adddate,areaid,status,linkurl,content) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (
                    item['type_id'], item['title'], item['source_name'], item['time'], item['web_time'],
                    item['addr_id'], 3, item['url'], pymysql.escape_string(item['intro']))

                self.cur.execute(sql)
                self.cur.fetchall()
                self.conn.commit()

        except Exception as e:
            print("数据上传失败")
            print(item['title'])
            print(item['url'])
            print(e)



    def close_spider(self, spider):
        self.conn.close()
