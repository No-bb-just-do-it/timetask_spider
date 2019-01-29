# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category
import re
from utils.STMP import send_mail_when_error
from utils.parse_content import pc

# http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006002/006002001/ @ 荆州市公共资源交易信息网
class jingzhouSpiderSpider(scrapy.Spider):
    name = 'jingzhou_city_gov_spider'

    def __init__(self):

        self.city_dict = get_city_dict()
        self.category = category

        self.baseUrl = 'http://www.jzggzy.com'

        self.xpath_rule = {
            'title_rule': './td[2]/a/@title',
            'url_rule': './td[2]/a/@href',
            'web_time_rule': './td[4]//text()',
            'content_rule' : r'id="TDContent" style="text-align:left;padding:10px;">(.*?)<!--网站底部-->'
        }

        self.error_count = 0
        self.source_name = '锦州市公共资源交易管理办公室'

        self.regularExpression = regularExpression
        self.regularExpression02 = regularExpression02

        self.addr_id = '430'

        self.headers = {
            'Host': 'www.jzggzy.com',
            'Referer': 'http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006002/006002002/?Paging=1'
        }

        self.pc = pc

        self.start_urls = [
            # 政府采购 招标公告83页 更正公告6页 中标结果75页 废标公告6页（每日更新均一页）
            ('招标公告', 'http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006002/006002001/?Paging={}', 3),
            ('变更公告', 'http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006002/006002002/?Paging={}', 3),
            ('招标结果', 'http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006002/006002003/?Paging={}', 3),
            ('招标结果', 'http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006002/006002005/?Paging={}', 3),
            # 市县信息 招标公告12页 澄清公告7页 评标结果公示11页 中标公告10页 （每日更新均一页）
            ('招标公告', 'http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006008/006008001/?Paging={}', 3),
            ('招标结果', 'http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006008/006008002/?Paging={}', 3),
            ('招标结果', 'http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006008/006008003/?Paging={}', 3),
            ('招标结果', 'http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006008/006008004/?Paging={}', 3),
            # 房建市政 招标公告49页 更正公告6页 评标结果公示43页 结果公示41页
            ('招标公告', 'http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006001/006001001/?Paging={}', 3),
            ('招标公告', 'http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006001/006001002/?Paging={}', 3),
            ('招标公告', 'http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006001/006001003/?Paging={}', 3),
            ('招标公告', 'http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006001/006001004/?Paging={}', 3)
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

        infos = response.xpath('//div[@class="con-list"]/table//tr[@height="24"]')

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