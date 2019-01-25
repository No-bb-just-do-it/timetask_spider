# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import time
import re
from utils.STMP import send_mail_when_error
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category

# http://www.dqgpc.gov.cn/jyxxZfcg/index_1.htm @ 大庆市公共资源交易网
class daqingSpiderSpider(scrapy.Spider):
    name = 'daqing_city_gov_spider'
    # allowed_domains = ['msggzy.org.cn']

    def __init__(self):

        self.city_dict = get_city_dict()
        self.regularExpression = regularExpression
        self.regularExpression02 = regularExpression02
        self.category = category

        self.govPurchase_baseUrl = 'http://www.dqgpc.gov.cn'

        self.error_count = 0

        self.start_urls = [
            # 政府采购公告 共843页 每天更新1页
            ('招标公告', 'http://www.dqgpc.gov.cn/jyxxZfcgCggg/index_{}.htm', 3),
            # 政府采购结果 共364页 每天更新1页
            ('招标结果', 'http://www.dqgpc.gov.cn/jyxxZfcgZbgg/index_{}.htm', 3),
            # 预中标公告 共402页 每天更新1页
            ('招标结果', 'http://www.dqgpc.gov.cn/jyxxZfcgYzbgg/index_{}.htm', 3),
            # 建设水利交通工程招标工程 共110页 每天更新1页
            ('招标公告', 'http://www.dqgpc.gov.cn/jyxxJsgcZbgg/index_{}.htm', 3),
            # 建设水利交通工程招标工程变更公告 共31页 每天更新1页
            ('变更公告', 'http://www.dqgpc.gov.cn/jyxxJsgcBgcggg/index_{}.htm', 3),
            # 建设水利交通工程招标工程结果公告 共133页 每天更新1页
            ('招标结果', 'http://www.dqgpc.gov.cn/jyxxJsgcZbgs/index_{}.htm', 3),
        ]

        self.headers = {
            'Host': 'www.dqgpc.gov.cn',
            'Referer': 'http://www.dqgpc.gov.cn/jyxxZfcg/index_1.htm'
        }


    def start_requests(self):
        for url_info in self.start_urls:
            urls = [url_info[1].format(i) for i in range(1, url_info[2])]
            for url in urls:
                items = {}
                items['type_id'] = self.category[url_info[0]]
                yield scrapy.Request(url, callback=self.parse, meta={"items": deepcopy(items)}, headers = self.headers)

    def parse(self, response):
        items = response.meta['items']
        # 由于最后一个tr标签为页数栏、所以排除掉
        all_lis = response.xpath('//div[@class="infor-con2 on"]//li')

        for each_li in all_lis:
            items['title'] = ''
            items['url'] = ''
            items['web_time'] = ''
            items['intro'] = ''
            items['addr_id'] = ''

            try:
                items['title'] = each_li.xpath('./a/@title').extract_first()
            except:
                pass

            try:
                # 因为有时候所获取的url没有带协议 有些就有有  所有加了个判断语句
                items['url'] = each_li.xpath('./a/@href').extract_first()
                if 'http' not in items['url']:
                    items['url'] = self.govPurchase_baseUrl + items['url']
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
                items['web_time'] = each_li.xpath('./span/text()').extract_first()
            except:
                pass

            if '.doc' not in items['url'] or '.rar' not in items['url'] or '.jpg' not in items['url'] or '.docx' not in items['url']:
                yield scrapy.Request(items['url'], callback = self.parse_article, meta = {'items' : deepcopy(items)}, headers = self.headers)


    def parse_article(self, response):
        items = response.meta['items']

        try:
            dirty_article = re.search(r'<body.*?>(.*?)</body>', response.text, re.S).group(1)
            clean_article = re.sub(self.regularExpression, ' ', dirty_article)
            items['intro'] = clean_article
        except:
            pass

        items['addr_id'] = '413'
        items["source_name"] = '大庆市公共资源交易网'

        yield items


