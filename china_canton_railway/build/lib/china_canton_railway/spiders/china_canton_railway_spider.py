# -*- coding: utf-8 -*-
# 中国铁路广州局集团有限公司物资采购商务平台
import scrapy
from copy import deepcopy
import time
import re


class ChinaCantonRailwaySpiderSpider(scrapy.Spider):
    name = 'china_canton_railway_spider'
    allowed_domains = []
    # start_urls = ['http://95306.cn/']

    def __init__(self):
        self.city_dict = {}
        # 将各个城市与编号制成字典
        with open('城市编号id.txt', 'r', encoding='GB2312')as f:
            city_data = f.read()
            for each_info in city_data.split('\n'):
                self.city_dict[each_info.split(',')[0]] = each_info.split(',')[1]
        # 采购公告
        self.purchase_notice_url = 'http://wz.guangzh.95306.cn/mainPageNoticeList.do?method=init&id=1000001&cur=1&keyword=&inforCode=&time0=&time1='
        # 中标公告
        self.bid_dealnotice_url = 'http://wz.guangzh.95306.cn/mainPageNoticeList.do?method=init&id=1200001&cur=1&keyword=&inforCode=&time0=&time1='
        # 文章拼接链接
        self.article_url = 'http://61.235.77.80/'

    def start_requests(self):
        # 采购公告
        # for page in range(1, 3):
        #     items = {}
        #     items['type_id'] = '38255'
        #     yield scrapy.Request(url = self.purchase_notice_url.format(str(page)), callback = self.parse, meta = {'items' : deepcopy(items)})

        #采购结果
        for page in range(1, 3):
            items = {}
            items['type_id'] = '38257'
            yield scrapy.Request(url = self.bid_dealnotice_url.format(str(page)), callback = self.parse, meta = {'items' : deepcopy(items)})


    def parse(self, response):
        items = response.meta['items']

        # 获取所有信息的所在tr标签
        all_trs = response.xpath('//table[@class="listInfoTable"]//tr')[1:]

        for each_tr in all_trs[3:8]:
            items = {}
            items['title'] = each_tr.xpath('./td/@title').extract_first().replace('\r', '')
            items['url'] = self.article_url + each_tr.xpath('./td/a/@href').extract_first()
            dirty_time = each_tr.xpath('./td/following-sibling::td[4]/@title').extract_first()
            # 将日期改成时间戳  '2018-11-30' ===> '1543507200'
            items['web_time'] = int(time.mktime(time.strptime(dirty_time, "%Y-%m-%d")))
            items['type_id'] = '38255'

            for city in self.city_dict:
                if city in items['title']:
                    items['addr'] = city
                    items['addr_id'] = self.city_dict[items['addr']]
                    break

            if 'addr' not in items:
                items['addr'] = '全国'
                items['addr_id'] = '400'

            yield scrapy.Request(url = items['url'], callback = self.parse_article, meta = {'items' : deepcopy(items)})


    def parse_article(self, response):
        items = response.meta['items']

        dirty_text = response.text

        dirty_article = re.search(r'<div class="topTlt">(.*?)<input type="hidden" name="flagForward"', dirty_text,
                                  re.S).group(1)
        clean_article = re.sub(r'\r|\t|\n', '', dirty_article)

        # 系统时间，时间戳
        items["time"] = '%.0f' % time.time()
        # 分类id
        items["sheet_id"] = '29'
        # 文章来源
        items["source_name"] = '中国铁路广州局集团有限公司物资采购商务平台'

        # items['intro'] = clean_article

        print(items)

