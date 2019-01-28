# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category
import re
from utils.STMP import send_mail_when_error

# http://ggzyjy.dl.gov.cn/TPFront/jyxx/071002/071002001/ @ 大连市公共资源
class dalianSpiderSpider(scrapy.Spider):
    name = 'dalian_city_gov_spider'

    def __init__(self):

        self.city_dict = get_city_dict()
        self.category = category

        self.baseUrl = 'http://ggzyjy.dl.gov.cn'

        self.xpath_rule = {
            'title_rule': './td[2]/a/text()',
            'url_rule': './td[2]/a/@href',
            'web_time_rule': './td[4]/text()',
            'content_rule' : r'id="mainContent">(.*?)<!-- footer -->'
        }

        self.error_count = 0
        self.source_name = '大连市公共资源'

        self.regularExpression = regularExpression
        self.regularExpression02 = regularExpression02

        self.addr_id = '411'

        self.headers = {
            'Host': 'ggzyjy.dl.gov.cn',
            'Referer': 'https://www.ggzyjy.dl.gov.cn'
        }

        self.start_urls = [
            # 政府采购
            ('招标公告', 'http://ggzyjy.dl.gov.cn/TPFront/jyxx/071002/071002001/?pageing={}', 3),
            ('招标结果', 'http://ggzyjy.dl.gov.cn/TPFront/jyxx/071002/071002003/?pageing={}', 3),
            ('招标公告', 'http://ggzyjy.dl.gov.cn/TPFront/jyxx/071002/071002005/?pageing={}', 3),
            # 建设工程
            ('招标公告', 'http://ggzyjy.dl.gov.cn/TPFront/jyxx/071001/071001001/?pageing={}', 3),
            ('招标结果', 'http://ggzyjy.dl.gov.cn/TPFront/jyxx/071001/071001002/?pageing={}', 3),
            ('招标结果', 'http://ggzyjy.dl.gov.cn/TPFront/jyxx/071001/071001003/?pageing={}', 3),
            # 卫计采购
            ('招标公告', 'http://ggzyjy.dl.gov.cn/TPFront/jyxx/071008/071008001/?pageing={}', 3),
            ('招标结果', 'http://ggzyjy.dl.gov.cn/TPFront/jyxx/071008/071008003/?pageing={}', 3),
            ('招标公告', 'http://ggzyjy.dl.gov.cn/TPFront/jyxx/071008/071008005/?pageing={}', 3),
        ]

        self.health_xpath = {
        'title_rule' : './div/a/text()',
        'url_rule' : './div/a/@href',
        'web_time_rule' : './span/text()',
        'content_rule': r'id="mainContent">(.*?)<!-- footer -->'
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

        if '071008' not in response.url:
            infos = response.xpath('//table[@class="ewb-trade-tb"]//tr')[1:]
        else:
            infos = response.xpath('//ul[@class="wb-data-item"]/li')

        if '071008' not in  response.url:
            self.xpath_rule = self.xpath_rule
        else:
            self.xpath_rule = self.health_xpath

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
                items['web_time'] = each_li.xpath(self.xpath_rule['web_time_rule']).extract_first().strip()
            except:
                pass
            yield scrapy.Request(items['url'], callback = self.parse_article, headers = self.headers, meta = {'items' : deepcopy(items)})


    def parse_article(self, response):

        items = response.meta['items']

        try:
            dirty_article = re.search(self.xpath_rule['content_rule'], response.text, re.S).group(1)
            dirty_article = re.sub(self.regularExpression02, '>', dirty_article)
            clean_article = re.sub(self.regularExpression, ' ', dirty_article)
            items['intro'] = clean_article
        except:
            pass

        if '更正' in items['title'] or '变更' in items['title']:
            items['type_id'] = '38256'

        items['addr_id'] = self.addr_id

        if items['addr_id'] == '':
            for city in self.city_dict:
                if city in items['title']:
                    items['addr_id'] = self.city_dict[city]
                    break

        items["source_name"] = self.source_name

        yield items






