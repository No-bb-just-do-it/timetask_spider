# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import re
from utils.STMP import send_mail_when_error
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, category
from .common_spider import CommonSpider

# http://www.airchina.com.cn/cn/contact_us/cgpt/cgxmgg/index.shtml @ 中国国际航空公司
class AirChinaSpiderSpider(CommonSpider):
    name = 'AirChina_spider'
    allowed_domains = ['airchina.com.cn']

    def __init__(self):

        self.city_dict = get_city_dict()
        self.regularExpression = regularExpression
        self.category = category

        self.base_url = 'http://www.airchina.com.cn'
        self.source_name = '中国国际航空公司'
        self.error_count = 0

        self.start_urls = [
            ('招标公告', 'http://www.airchina.com.cn/cn/contact_us/cgpt/cgxmgg/index.shtml', 3)
        ]
        self.headers = {
            'Connection': 'keep-alive',
            'Host': 'www.airchina.com.cn',
        }
        self.xpath_rule = {
            'content_rule' : r'<!--AutonomyContentBegin-->(.*?)<!--AutonomyContentEnd-->'
        }

    def start_requests(self):
        # 因为看了一下国航官网 发现只有一页
        items = {}
        items["type_id"] = self.category[self.start_urls[0][0]]
        yield scrapy.Request(self.start_urls[0][1], callback=self.parse, meta={"items": deepcopy(items)}, headers = self.headers)

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



