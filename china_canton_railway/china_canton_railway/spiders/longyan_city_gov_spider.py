# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import time
import re
from utils.STMP import send_mail_when_error
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category

# https://www.lyggzy.com.cn/lyztb/zfcg/082003/082003001/ @ 龙岩市公共资源交易网
class longyanSpiderSpider(scrapy.Spider):
    name = 'longyan_city_gov_spider'
    # allowed_domains = ['msggzy.org.cn']

    def __init__(self):

        self.city_dict = get_city_dict()
        self.regularExpression = regularExpression
        self.regularExpression02 = regularExpression02
        self.category = category

        self.govPurchase_baseUrl = 'https://www.lyggzy.com.cn'

        self.error_count = 0

        self.headers = {
            'Host': 'www.lyggzy.com.cn',
            'Referer': 'https://www.lyggzy.com.cn/lyztb/zfcg/082003/082003001/'
        }

        self.start_urls = [
            # 政府采购公告 共241页、 每天更新跨度1页
            ('招标公告', 'https://www.lyggzy.com.cn/lyztb/zfcg/082003/082003001/?pageing={}', 3),
            # 政府采购结果 共171页、 每天更新跨度1页
            ('招标结果', 'https://www.lyggzy.com.cn/lyztb/zfcg/082003/082003002/?pageing={}', 3),
            # 政府采购中其他采购 共25页 每天更新跨度1页
            ('招标公告', 'https://www.lyggzy.com.cn/lyztb/zfcg/082001/082001002/?pageing={}', 3),
            # 政府采购中其他采购结果 共16页 每天更新跨度1页
            ('招标结果', 'https://www.lyggzy.com.cn/lyztb/zfcg/082001/082001003/?pageing={}', 3),
            # 工程建设招标信息 共86页 每天更新跨度1页
            ('招标公告', 'https://www.lyggzy.com.cn/lyztb/gcjs/081001/081001010/?pageing={}', 3),
            # 工程建设招标结果  共86页 每天更新跨度1页
            ('招标结果', 'https://www.lyggzy.com.cn/lyztb/gcjs/081001/081001010/?pageing={}', 3),
            # 工程建设评标结果公示 共151 每天更新跨度1页
            ('招标结果', 'https://www.lyggzy.com.cn/lyztb/gcjs/081001/081001005/?pageing={}', 3),
        ]

    def start_requests(self):
        for url_info in self.start_urls:
            urls = [url_info[1].format(i) for i in range(1, url_info[2])]
            for url in urls:
                items = {}
                items['type_id'] = self.category[url_info[0]]
                yield scrapy.Request(url, callback=self.parse, meta={"items": deepcopy(items)}, headers = self.headers)

    def parse(self, response):
        items = response.meta['items']
        # 获取所有招标信息的li标签
        all_lis = response.xpath('//div[@class="r-bd"]/ul[1]/li')

        for each_li in all_lis:
            items['title'] = ''
            items['url'] = ''
            items['web_time'] = ''
            items['intro'] = ''
            items['addr_id'] = ''

            try:
                if ']' in items['title']:
                    items['title'] = each_li.xpath('./a/text()').extract_first().strip().split(']')[1]
                else:
                    items['title'] = each_li.xpath('./a/text()').extract_first().strip()
            except:
                pass

            try:
                items['url'] = self.govPurchase_baseUrl + each_li.xpath('./a/@href').extract_first()
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
                items['web_time'] = each_li.xpath('.//span/text()').extract_first().strip()
            except:
                pass

            yield scrapy.Request(items['url'], callback = self.parse_article, meta = {'items' : deepcopy(items)}, headers = self.headers)


    def parse_article(self, response):
        items = response.meta['items']

        try:
            dirty_article = re.search(r'<div class="substance" id="mainContent">(.*?)<!-- 各类公告信息 -->', response.text, re.S).group(1)
            dirty_article = re.sub(self.regularExpression02, '>', dirty_article)
            clean_article = re.sub(self.regularExpression, ' ', dirty_article)
            items['intro'] = clean_article
        except:
            pass

        if '更正' in items['title'] or '变更' in items['title']:
            items['type_id'] = '38256'

        items['addr_id'] = '403'
        items["source_name"] = '龙岩市公共资源交易网'

        yield items