# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category
import re
from utils.STMP import send_mail_when_error
from utils.parse_content import pc

class CommonSpider(scrapy.Spider):

    def __init__(self):
        self.regularExpression = regularExpression
        self.regularExpression02 = regularExpression02
        self.category = category

        self.xpath_rule = {
            'list_page': '',
            'title_rule': '',
            'url_rule': '',
            'web_time_rule': '',
            'content_rule': r''
        }
        self.city_dict = get_city_dict()
        self.pc = pc
        self.source_name = ''
        self.addr_id = ''
        self.error_count = ''
        self.baseUrl = ''
        self.headers = {}

    def start_requests(self):
        for url_info in self.start_urls:
            urls = [url_info[1].format(i) for i in range(1, url_info[2])]
            for url in urls:
                items = {}
                items['type_id'] = self.category[url_info[0]]
                yield scrapy.Request(url, callback=self.parse, meta={"items": deepcopy(items)}, headers = self.headers)

    def parse(self, response):
        items = response.meta['items']

        infos = response.xpath(self.xpath_rule['list_page'])

        for each_li in infos:
            items['title'] = ''
            items['url'] = ''
            items['web_time'] = ''
            items['intro'] = ''
            items['addr_id'] = ''

            try:
                items['title'] = ''.join(each_li.xpath(self.xpath_rule['title_rule']).extract()).strip()
            except:
                pass

            try:
                items['url'] = self.baseUrl + each_li.xpath(self.xpath_rule['url_rule']).extract_first()
                if items['url'] == None:
                    raise Exception
            except:
                msg = self.name + ', 该爬虫详情页获取url失败'
                # send_mail_when_error(msg)
                self.error_count += 1
                if self.error_count > 3:
                    quit()
                    msg = self.name + ', 该爬虫因详情页获取失败被暂停'
                    # send_mail_when_error(msg)
                pass

            try:
                items['web_time'] = each_li.xpath(self.xpath_rule['web_time_rule']).extract_first().strip()
            except:
                pass
            # print(items)
            yield scrapy.Request(items['url'], callback = self.parse_article, headers = self.headers, meta = {'items' : deepcopy(items)})


    def parse_article(self, response):
        items = response.meta['items']
        try:
            dirty_article = re.search(self.xpath_rule['content_rule'], response.text, re.S).group(1)
            dirty_article = re.sub(regularExpression02, '>', dirty_article)
            clean_article = re.sub(regularExpression, ' ', dirty_article)
            items['intro'] = clean_article
        except:
            pass

        items['addr_id'] = self.addr_id
        if items['addr_id'] == '':
            for city in self.city_dict:
                if city in items['title']:
                    items['addr_id'] = self.city_dict[city]
                    break

        if '中标' in items['title']:
            items['type_id'] = '38257'
        elif '更正' in items['title'] or '变更' in items['title']:
            items['type_id'] = '38256'

        if items['addr_id'] == '':
            for city in self.city_dict:
                if city in items['title']:
                    items['addr_id'] = self.city_dict[city]
                    break

        items["source_name"] = self.source_name
        yield items