# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import time
import re
from utils.STMP import send_mail_when_error
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category

# http://zhuzhou.hnsggzy.com/jygkzfcg/index_1.jhtml @ 株洲市公共资源交易网
class zhuzhouSpiderSpider(scrapy.Spider):
    name = 'zhuzhou_city_gov_spider'
    # allowed_domains = ['msggzy.org.cn']

    def __init__(self):

        self.city_dict = get_city_dict()
        self.regularExpression = regularExpression
        self.regularExpression02 = regularExpression02
        self.category = category

        self.govPurchase_baseUrl = 'http://www.dqgpc.gov.cn'

        self.error_count = 0

        self.start_urls = [
            # 政府采购类 包含采购公告、采购结果 共273页 每天更新1页
            ('招标公告', 'http://zhuzhou.hnsggzy.com/jygkzfcg/index_{}.jhtml', 3),
            # 工程建设类 包含公告、结果、  共200页 每天更新1页
            ('招标公告', 'http://zhuzhou.hnsggzy.com/gczb/index_{}.jhtml', 3),
        ]

        self.headers = {
            'Host': 'zhuzhou.hnsggzy.com',
            'Referer': 'http://zhuzhou.hnsggzy.com/jygkzfcg/index_2.jhtml'
        }

    def start_requests(self):
        for url_info in self.start_urls:
            # 构造分页列表
            urls = [url_info[1].format(i) for i in range(1, url_info[2])]
            for url in urls:
                items = {}
                items["type_id"] = self.category[url_info[0]]
                yield scrapy.Request(url, callback=self.parse, meta={"items": deepcopy(items)}, headers = self.headers)

    def parse(self, response):
        items = response.meta['items']

        # 获取所有招标信息的li标签
        all_lis = response.xpath('//div[@class="article-content"]/ul/li')

        for each_li in all_lis:
            items['title'] = ''
            items['url'] = ''
            items['web_time'] = ''
            items['intro'] = ''
            items['addr_id'] = ''

            try:
                items['title'] = ''.join(each_li.xpath('./div[1]/a//text()').extract())
            except:
                pass

            try:
                items['url'] = each_li.xpath('./div[1]/a/@href').extract_first()
                if items['url'] == None:
                    raise Exception
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
                items['web_time'] = each_li.xpath('./div[1]//div/text()').extract_first().strip()
            except:
                pass

            yield scrapy.Request(items['url'], callback = self.parse_article, meta = {'items' : deepcopy(items)}, headers = self.headers)


    def parse_article(self, response):
        items = response.meta['items']

        try:
            dirty_article = re.search(r'<div class="content">(.*?)<span><a href="', response.text, re.S).group(1)
            dirty_article = re.sub(self.regularExpression02, '>', dirty_article)
            clean_article = re.sub(self.regularExpression, ' ', dirty_article)
            items['intro'] = clean_article
        except:
            pass

        if '中标' in items['title']:
            items['type_id'] = '38257'
        elif '更正' in items['title'] or '变更' in items['title']:
            items['type_id'] = '38256'

        items['addr_id'] = '431'
        items["source_name"] = '株洲市公共资源交易网'

        yield items