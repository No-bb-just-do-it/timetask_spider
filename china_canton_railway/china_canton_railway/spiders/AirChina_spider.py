# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import time
import re
from utils.STMP import send_mail_when_error
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, category

# http://www.airchina.com.cn/cn/contact_us/cgpt/cgxmgg/index.shtml @ 中国国际航空公司
class AirChinaSpiderSpider(scrapy.Spider):
    name = 'AirChina_spider'
    allowed_domains = ['airchina.com.cn']

    def __init__(self):

        self.city_dict = get_city_dict()
        self.regularExpression = regularExpression
        self.category = category

        self.base_url = 'http://www.airchina.com.cn'

        self.error_count = 0

        self.start_urls = [
            ('招标公告', 'http://www.airchina.com.cn/cn/contact_us/cgpt/cgxmgg/index_{}.shtml', 3)
        ]

        self.headers = {
            'Connection': 'keep-alive',
            'Host': 'www.airchina.com.cn',
        }


    def start_requests(self):
        for url_info in self.start_urls:
            # 构造分页列表
            urls = [url_info[1].format(i) for i in range(1, url_info[2])]
            for url in urls:
                if 'index_1' in url:
                    url = 'http://www.airchina.com.cn/cn/contact_us/cgpt/cgxmgg/index.shtml'
                items = {}
                items["type_id"] = self.category[url_info[0]]
                yield scrapy.Request(url, callback=self.parse, meta={"items": deepcopy(items)}, headers = self.headers)

    def parse(self, response):

        items = response.meta['items']
        # 获取所有招标信息的li标签
        all_lis = response.xpath('//div[@class="serviceMsg"]//ul/li')

        for each_li in all_lis:
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
                items['url'] = self.base_url + each_li.xpath('./a/@href').extract_first()
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
                # (2017-05-31)日期格式
                dirty_time = each_li.xpath('.//span/text()').extract_first()
                items['web_time'] = re.sub('\(|\)', '', dirty_time).strip()
            except:
                pass

            yield scrapy.Request(items['url'], callback = self.parse_article, meta = {'items' : deepcopy(items)}, headers = self.headers)


    def parse_article(self, response):
        items = response.meta['items']

        try:
            dirty_article = re.search(r'<!--AutonomyContentBegin-->(.*?)<!--AutonomyContentEnd-->', response.text, re.S).group(1)
            clean_article = re.sub(self.regularExpression, ' ', dirty_article)
            items['intro'] = clean_article
        except:
            pass

        for city in self.city_dict:
            if city in items['title']:
                items['addr_id'] = self.city_dict[city]
                break

        # 文章来源
        items["source_name"] = '中国国际航空公司'

        yield items



