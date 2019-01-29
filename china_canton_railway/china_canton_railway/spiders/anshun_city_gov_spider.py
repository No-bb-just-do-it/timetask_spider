# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category
import re
from utils.STMP import send_mail_when_error
from utils.parse_content import pc

# http://www.ggzy.anshun.gov.cn/jyxx/003002/003002001/1.html @ 安顺市全国公共资源交易平台
class anshunSpiderSpider(scrapy.Spider):
    name = 'anshun_city_gov_spider'

    def __init__(self):

        self.city_dict = get_city_dict()
        self.category = category

        self.baseUrl = 'http://www.ggzy.anshun.gov.cn'

        self.xpath_rule = {
            'title_rule': './div/a/text()',
            'url_rule': './div/a/@href',
            'web_time_rule': './span/text()',
            'content_rule' : r'<div class="ewb-list-bd">(.*?)<!-- 分享 BEGIN -->'
        }

        self.error_count = 0
        self.source_name = '安顺市全国公共资源交易平台'

        self.regularExpression = regularExpression
        self.regularExpression02 = regularExpression02

        self.addr_id = '425'

        self.headers = {
            'Host': 'www.ggzy.anshun.gov.cn',
            'Referer': 'www.ggzy.anshun.gov.cn'
        }

        self.pc = pc

        self.start_urls = [
            # 政府采购 招标公告110页 交易结果公示87页 废标公告30页 资审结果公示2页 答疑澄更16页
            ('招标公告', 'http://www.ggzy.anshun.gov.cn/jyxx/003002/003002001/{}.html', 3),
            ('招标结果', 'http://www.ggzy.anshun.gov.cn/jyxx/003002/003002002/{}.html', 3),
            ('招标结果', 'http://www.ggzy.anshun.gov.cn/jyxx/003002/003002003/{}.html', 3),
            ('招标结果', 'http://www.ggzy.anshun.gov.cn/jyxx/003002/003002004/{}.html', 3),
            ('招标公告', 'http://www.ggzy.anshun.gov.cn/jyxx/003002/003002005/{}.html', 3),
            # 建设工程 招标公告396页 交易结果公示313 废标公告42页
            ('招标公告', 'http://www.ggzy.anshun.gov.cn/jyxx/003001/003001001/{}.html', 3),
            ('招标结果', 'http://www.ggzy.anshun.gov.cn/jyxx/003001/003001002/{}.html', 3),
            ('招标结果', 'http://www.ggzy.anshun.gov.cn/jyxx/003001/003001003/{}.html', 3),
        ]


    def start_requests(self):
        for url_info in self.start_urls:
            urls = [url_info[1].format(i) for i in range(1, url_info[2])]
            for url in urls:
                items = {}
                items['type_id'] = self.category[url_info[0]]
                yield scrapy.Request(url, callback=self.parse, meta={"items": deepcopy(items)}, headers=self.headers)


    def parse(self, response):
        items = response.meta['items']

        infos = response.xpath('//div[@class="ewb-right-bd"]/ul/li')

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
            yield scrapy.Request(items['url'], callback=self.parse_article, headers=self.headers,
                                 meta={'items': deepcopy(items)})

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