# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import time
import re
from utils.STMP import send_mail_when_error
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, category

# http://www.yueyang.gov.cn/cxjs/zbtb/default.htm @ 岳阳市人民政府
class yueyangSpiderSpider(scrapy.Spider):
    name = 'yueyang_city_gov_spider'
    allowed_domains = ['yueyang.gov.cn']

    def __init__(self):

        self.city_dict = get_city_dict()
        self.regularExpression = regularExpression
        self.category = category

        self.govPurchase_baseUrl = 'http://www.yueyang.gov.cn/cxjs/zbtb/'
        self.construction_baseUrl = 'http://www.yueyang.gov.cn/cxjs/12112/24215/24216/'

        self.error_count = 0

        self.start_urls = [
            # 政府采购739 每天两页 工程建设207 每天一页 医疗采购49 每天一页
            ('招标结果', 'http://www.yueyang.gov.cn/cxjs/zbtb/default.jsp?pager.offset={}&pager.desc=false', 3),
            ('招标结果', 'http://www.yueyang.gov.cn/cxjs/12112/24215/24216/default.jsp?pager.offset={}&pager.desc=false', 3),
            ('招标结果', 'http://www.yueyang.gov.cn/cxjs/12112/24215/24217/default.jsp?pager.offset={}&pager.desc=false', 3),
        ]

        self.headers = {
            'Connection': 'keep-alive',
            'Host': 'www.yueyang.gov.cn'
        }

    def start_requests(self):
        for url_info in self.start_urls:
            # 构造分页列表 index_1为第二页 index_2为第三页
            urls = [url_info[1].format(i * 15) for i in range(0, url_info[2])]
            for url in urls:
                items = {}
                items['type_id'] = self.category[url_info[0]]
                yield scrapy.Request(url, callback=self.parse, meta={"items": deepcopy(items)}, headers = self.headers, dont_filter=True)

    def parse(self, response):

        items = response.meta['items']
        # 获取所有招标信息的li标签
        all_lis = response.xpath('//div[@style="display: block;"]//li')

        for each_li in all_lis[:3]:
            items['title'] = ''
            items['url'] = ''
            items['web_time'] = ''
            items['intro'] = ''
            items['addr_id'] = ''

            try:
                items['title'] = each_li.xpath('./a/text()').extract_first()
            except:
                pass

            try:
                if 'zbtb' in response.url:
                    items['url'] = each_li.xpath('./a/@href').extract_first()
                elif '24216' in response.url:
                    items['url'] = each_li.xpath('./a/@href').extract_first()
                elif '24217' in response.url:
                    items['url'] = each_li.xpath('./a/@href').extract_first()
            except:
                msg = self.name + ', 该爬虫详情页获取url失败'
                send_mail_when_error(msg)
                self.error_count += 1
                if self.error_count > 3:
                    quit()
                    msg = self.name + ', 该爬虫因详情页获取失败被暂停'
                    send_mail_when_error(msg)
                pass

            try:
                items['web_time'] = each_li.xpath('./span[@class="time"]/text()').extract_first().strip()
            except:
                pass

            yield scrapy.Request(items['url'], callback = self.parse_article, headers = self.headers, meta = {'items' : deepcopy(items)})


    def parse_article(self, response):
        items = response.meta['items']

        if '招标公告' in items['title']:
            items['type_id'] = '38255'
        elif '变更' in items['title'] or '更正' in items['title']:
            items['type_id'] = '38256'

        try:
            dirty_article = re.search(r'<div class="content_" id="zoom">(.*?)<!--底部-->', response.text, re.S).group(1)
            clean_article = re.sub(self.regularExpression, ' ', dirty_article)
            items['intro'] = clean_article
        except:
            pass

        items['addr_id'] = '431'
        items["source_name"] = '岳阳市人民政府'

        yield items



