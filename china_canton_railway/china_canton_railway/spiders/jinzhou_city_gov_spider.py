# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category
import re
from utils.STMP import send_mail_when_error
from utils.parse_content import pc

# http://www.jztb.gov.cn/jyxx/077001/077001001/1.html @ 锦州市公共资源交易管理办公室
class jinzhouSpiderSpider(scrapy.Spider):
    name = 'jinzhou_city_gov_spider'

    def __init__(self):

        self.city_dict = get_city_dict()
        self.category = category

        self.baseUrl = 'http://www.jztb.gov.cn'

        self.xpath_rule = {
            'title_rule': './/a/text()',
            'url_rule': './/a/@href',
            'web_time_rule': './span/text()',
            'content_rule' : r'<div class="news-article">(.*?)<!-- footer -->'
        }

        self.error_count = 0
        self.source_name = '锦州市公共资源交易管理办公室'

        self.regularExpression = regularExpression
        self.regularExpression02 = regularExpression02

        self.addr_id = '411'

        self.headers = {
            'Host': 'www.jztb.gov.cn',
            'Referer': 'www.jztb.gov.cn'
        }

        self.pc = pc

        self.start_urls = [
            # 政府采购 公告共397页 结果共258 变更共14页（更新频率均1页）
            ('招标公告', 'http://www.jztb.gov.cn/jyxx/077001/077001001/{}.html', 3),
            ('招标结果', 'http://www.jztb.gov.cn/jyxx/077001/077001002/{}.html', 3),
            ('变更公告', 'http://www.jztb.gov.cn/jyxx/077001/077001003/{}.html', 3),
            # 工程建设 招标公告112 中标候选人72 中标公示61（更新频率均1页）
            ('招标公告', 'http://www.jztb.gov.cn/jyxx/077002/077002001/{}.html', 3),
            ('招标结果', 'http://www.jztb.gov.cn/jyxx/077002/077002002/{}.html', 3),
            ('招标结果', 'http://www.jztb.gov.cn/jyxx/077002/077002003/{}.html', 3),
            # 药品器械采购公告 采购结果 均13页
            ('招标公告', 'http://www.jztb.gov.cn/jyxx/077005/077005001/{}.html', 3),
            ('招标结果', 'http://www.jztb.gov.cn/jyxx/077005/077005002/{}.html', 3),

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

        infos = response.xpath('//div[@id="jt"]/ul/li')

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
            items['intro'] = self.pc.get_clean_content(self.xpath_rule['content_rule'], self.regularExpression, self.regularExpression02, response.text)
        except:
            pass


        items['addr_id'] = self.addr_id

        if items['addr_id'] == '':
            for city in self.city_dict:
                if city in items['title']:
                    items['addr_id'] = self.city_dict[city]
                    break

        items["source_name"] = self.source_name
        yield items