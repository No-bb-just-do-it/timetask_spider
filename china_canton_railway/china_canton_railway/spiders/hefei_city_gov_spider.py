# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category
import re
from utils.STMP import send_mail_when_error
from utils.parse_content import pc

# http://zwgk.hefei.gov.cn/zwgk/public/index.xp?doAction=zdlylist2&type=5&id=001000180002&curPage=1 @ 合肥市政府信息公开网
class hefeiSpiderSpider(scrapy.Spider):
    name = 'hefei_city_gov_spider'

    def __init__(self):

        self.city_dict = get_city_dict()
        self.category = category

        self.baseUrl = 'http://zwgk.hefei.gov.cn'

        self.xpath_rule = {
            'title_rule': './/tr/td[2]/a/text()',
            'url_rule': './/tr/td[2]/a/@href',
            'web_time_rule': './/tr/td[3]//text()',
            'content_rule' : r'style="font-weight:bold;">(.*?)<!-- GWD SHARE BEGIN 文章底部-->'
        }

        self.error_count = 0
        self.source_name = '合肥市政府信息公开网'

        self.regularExpression = regularExpression
        self.regularExpression02 = regularExpression02

        self.addr_id = '402'

        self.headers = {
            'Host': 'zwgk.hefei.gov.cn',
            'Referer': 'http://zwgk.hefei.gov.cn/zwgk/public/index.xp?doAction=zdlylist2&type=5&id=001000180002'
        }

        self.pc = pc

        self.start_urls = [
            # 政府采购 招标公告 共1471页 中标公示 共1816页 每天更新跨度分别是（2，3）页 可以写6页
            ('招标公告', 'http://zwgk.hefei.gov.cn/zwgk/public/index.xp?doAction=zdlylist2&type=5&id=001000180002&curPage={}', 3),
            ('招标结果', 'http://zwgk.hefei.gov.cn/zwgk/public/index.xp?doAction=zdlylist2&type=5&id=001000180003&curPage={}', 3),
            # 工程招标 招标公告 共1342页 中标公示 共900页 每天更新跨度均3页 可以写5页
            ('招标公告','http://zwgk.hefei.gov.cn/zwgk/public/index.xp?doAction=zdlylist2&type=5&id=001000190002&curPage={}', 3),
            ('招标结果','http://zwgk.hefei.gov.cn/zwgk/public/index.xp?doAction=zdlylist2&type=5&id=001000190003&curPage={}', 3),
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
        infos = response.xpath('//form[@name="form1"]/table/tr[3]//table')

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
            # print(items)
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