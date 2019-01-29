# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category
import re
from utils.STMP import send_mail_when_error
from utils.parse_content import pc

# http://ggzy.gzlps.gov.cn/jyxxzc/index_1.jhtml @ 六盘水市公共资源交易网
class liupanshuiSpiderSpider(scrapy.Spider):
    name = 'liupanshui_city_gov_spider'

    def __init__(self):

        self.city_dict = get_city_dict()
        self.category = category

        self.baseUrl = ''

        self.xpath_rule = {
            'title_rule': './p[1]/a/text()',
            'url_rule': './p[1]/a/@href',
            'web_time_rule': './p[2]/text()',
            'content_rule' : r'</P>(.*?)<!--EndFragment-->'
        }

        self.error_count = 0
        self.source_name = '六盘水市公共资源交易网'

        self.regularExpression = regularExpression
        self.regularExpression02 = regularExpression02

        self.addr_id = '425'

        self.headers = {
            'Host': 'ggzy.gzlps.gov.cn',
            'Referer': 'http://ggzy.gzlps.gov.cn/jyxxzc/index.jhtml'
        }

        self.pc = pc

        self.start_urls = [
            ('招标公告', 'http://ggzy.gzlps.gov.cn/jyxxzc/index_{}.jhtml', 3)
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

        infos = response.xpath('//ul[@class="erul"]/li')

        for each_li in infos:
            items['title'] = ''
            items['url'] = ''
            items['web_time'] = ''
            items['intro'] = ''
            items['addr_id'] = ''

            try:
                items['title'] = each_li.xpath(self.xpath_rule['title_rule']).extract_first().strip()
            except:
                pass

            try:
                items['url'] = self.baseUrl + each_li.xpath(self.xpath_rule['url_rule']).extract_first()
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
                items['web_time'] = re.sub('\.', '-', each_li.xpath(self.xpath_rule['web_time_rule']).extract_first().strip())
            except:
                pass

            print(items)
            # yield scrapy.Request(items['url'], callback = self.parse_article, headers = self.headers, meta = {'items' : deepcopy(items)})