# -*- coding: utf-8 -*-
#http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=1&start_time=&end_time=&timeType=2&searchparam=&searchchannel=0&dbselect=bidx&kw=&bidSort=0&pinMu=0&bidType=0&buyerName=&projectId=&displayZone=&zoneId=&agentName=
from copy import deepcopy
import logging
import scrapy
from datetime import datetime, date, timedelta
import time
import re

from scrapy.exceptions import CloseSpider
from scrapy_redis.spiders import RedisSpider
import redis
from STMP import send_mail_when_error
# import os
# sys.path.append('/root/RegularExpression')
# from RegularExpression.custom_Re import ReguluarE

class ChinaGovComprehensiveSpider(scrapy.Spider):
    name = 'china_gov_comprehensive'
    allowed_domains = ['ccgp.gov.cn']
    # start_urls = ['http://ccgp.gov.cn/']
    # redis_key = 'amazonCategory:start_urls'

    def __init__(self):
        self.article_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Host': 'www.ccgp.gov.cn',
            'Referer': 'http://www.ccgp.gov.cn/',
            'Connection': 'keep-alive',
            # 'Accept-Language': 'en-GB,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            # 'Accept-Encoding': 'gzip, deflate'
        }

        self.city_dict = {}
        # 将各个城市与编号制成字典
        with open('城市编号id.txt', 'r', encoding = 'gb2312')as f:
            city_data = f.read()
            for each_info in city_data.split('\n'):
                self.city_dict[each_info.split(',')[0]] = each_info.split(',')[1]

        with open('/root/RegularExpression.txt', 'r')as f:
            self.regularExpression = f.read()

        self.category_dict = {
            '公开招标公告': '38255', '询价公告': '38255', '竞争性谈判公告': '38255', '单一来源': '38255', '资格预审': '38254', '邀请公告': '38255',
            '其它公告':'38255', '竞争性磋商公告': '38255', '中标公告': '38257', '更正公告': '38256', '成交公告': '38257', '废标流标': '38257', '终止公告' : '38257', '单一来源公告': '38255', '资格预审公告': '38254',  '其他公告':'38255', '邀请招标公告' : '38255'
        }

        # 用来计数获取详情页失败次数
        self.error_count = 0

        # 下载链接的url拼接
        self.download_page = 'http://www.ccgp.gov.cn/oss/download?uuid={}'

        # 生成html的a标签 用于下载附件链接
        self.html5 = '<a href = {}>下载附件</a>'

        #由于网页由脚本生成 所以无需在这里使用
        # 获取当日时间
        today = str(date.today())
        self.require_today = today.replace('-', ':')
        
        # 获取一年前的时间
        last_five_days = date.today() + timedelta(days = -7)
        last_five_days = str(last_five_days)
        self.last_five_days = last_five_days.replace('-', ':')

        # start_time代表上一年的时间 end_time代表今年的时间
        self.url = 'http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index={}&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=0&dbselect=bidx&kw=&start_time={}&end_time={}&timeType=6&displayZone=&zoneId=&pppStatus=0&agentName='
        self.save_url = 'http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index={}&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=0&dbselect=bidx&kw=&start_time=2018%3A10%3A13&end_time=2019%3A01%3A13&timeType=4&displayZone=&zoneId=&pppStatus=0&agentName='

    def quit(self):
        raise CloseSpider('close spider')

    # 使用redis就不用使用该函数创建request
    def start_requests(self):
        # 所有分类的综合  每天大概数据量在450页左右  设置页数161
        for page in range(1, 451):
            url = self.url.format(page, self.last_five_days, self.require_today)
            # print(url)
            yield scrapy.Request(url, callback = self.parse, dont_filter=True)
            # yield scrapy.Request(url = self.save_url.format(page), callback = self.parse, dont_filter=True)

    def parse(self, response):
        # 获取各个li标签  各条信息都在li标签中
        all_lis = response.xpath('//ul[@class="vT-srch-result-list-bid"]/li')
        # 遍历各个li标签
        for each_li in all_lis:
            items = {}

            items['title'] = ''
            items['url'] = ''
            items['web_time'] = ''
            items['intro'] = ''
            items['addr_id'] = ''

            try:
                items['title'] = each_li.xpath('./a/text()').extract_first().strip()
            except:
                pass

            try:
                items['url'] = each_li.xpath('./a/@href').extract_first()
            except:
                msg = self.name + ', 该爬虫详情页获取url失败'
                send_mail_when_error(msg)
                self.error_count += 1
                if self.error_count > 3:
                    self.quit()
                    msg = self.name + ', 该爬虫因详情页获取失败被暂停'
                    send_mail_when_error(msg)
                pass

            try:
                items['web_time'] = each_li.xpath('./span/text()').extract_first().split(' ')[0].replace('.', '-')
            except:
                pass

            try:
                items['addr'] = each_li.xpath('.//span//a/text()').extract_first()
            except:
                pass

            try:
                # 获取招标种类
                category = each_li.xpath('.//strong/text()').extract_first().strip()
            except:
                pass

            # 五位数的ID
            try:
                items['type_id'] = self.category_dict[category]
            except:
                print('*' * 50)

            if items['addr'] != None:
                for city in self.city_dict:
                    if city in items['addr']:
                        items['addr_id'] = self.city_dict[city]
                        break

            # print(items['addr'], category, items['type_id'])

            yield scrapy.Request(items['url'], headers = self.article_headers, callback = self.parse_article, meta = {'items' : deepcopy(items)})


    def parse_article(self, response):
        items = response.meta['items']

        dirty_article = response.text
        # 先设置一个空的字符串
        uuid = ''
        # 因为不是每个文章都有下载附件  所以使用try
        try:
            uuid = re.search(r"<a class='bizDownload' href='' id='(.*?)'", dirty_article).group(1)
        except:
            pass
        else:
            download_page = self.download_page.format(uuid)

        try:
            dirty_article = re.search(r'<div class="vF_detail_content_container">(.*?)<h2><p>相关公告</p></h2>', dirty_article, re.S).group(1)

            # 将附件链接拼接到文章中
            if uuid != '':
                dirty_article = dirty_article + '\n' + self.html5.format(download_page)

            # 利用正则清除垃圾数据(单机版)
            # clean_article = re.sub(r'\r|\t|\n|<!--.*?-->|<input.*?>|class=[\'\"].*?[\'\"]|id=[\'\"].*?[\'\"]|style=[\'\"].*?[\'\"]|<STYLE.*?>.*?<\/STYLE>|class=\w*', ' ', dirty_article)
            # 将文章的垃圾数据进行清洗（服务器版）
            clean_article = re.sub(eval(self.regularExpression), ' ', dirty_article)
        except:
            pass

        if items['addr_id'] == '':
            for city in self.city_dict:
                if city in items['title']:
                    items['addr_id'] = self.city_dict[city]

        if items['addr_id'] == '':
            items['addr_id'] = '100'


        # 系统时间，时间戳
        items["time"] = '%.0f' % time.time()
        # 分类id
        items["sheet_id"] = '29'
        # 文章来源
        items["source_name"] = '中国政府采购网'
        # 内容
        items["intro"] = clean_article
        # print(items)
        yield items

