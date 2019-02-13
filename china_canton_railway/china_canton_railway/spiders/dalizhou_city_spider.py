# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category
import re
from utils.STMP import send_mail_when_error
from utils.parse_content import pc

# https://www.dlggzy.cn/jyxx/zfcg/cggg?currentPage=1&area=013&scrollValue=0 @ 大理州公共资源交易电子服务系统
class dalizhouSpiderSpider(scrapy.Spider):
    name = 'dalizhou_city_gov_spider'

    def __init__(self):

        self.city_dict = get_city_dict()
        self.category = category

        self.baseUrl = 'https://www.dlggzy.cn'

        self.xpath_rule = {
            'title_rule': './td[3]/a/@title',
            'url_rule': './td[3]/a/@href',
            'web_time_rule': './td[4]/text()',
            'modify_url_rule' : './td[4]/a/@href',
            'modify_title_rule' : './td[4]/a/@title',
            'modify_web_time_rule' : './td[5]//text()',
            'result_title_rule' : './td[3]/@title',
            'content_rule' : r'<div class="news-title">(.*?)<div class="foot row">'
        }

        self.error_count = 0
        self.source_name = '大理州公共资源交易电子服务系统'

        self.regularExpression = regularExpression
        self.regularExpression02 = regularExpression02

        self.addr_id = '427'

        self.headers = {
            'Host': 'www.dlggzy.cn',
            'Referer': 'https://www.dlggzy.cn/jyxx/zfcg/cggg'
        }

        self.pc = pc

        self.start_urls = [
            # 政府采购 采购公告 共146页 变更通知共46页 结果公告121页 每天更新跨度均1页
            ('招标公告', 'https://www.dlggzy.cn/jyxx/zfcg/cggg?currentPage={}&area=013&scrollValue=0', 146),
            ('变更公告', 'https://www.dlggzy.cn/jyxx/zfcg/gzsx?currentPage={}&area=013&scrollValue=0', 46),
            ('招标结果', 'https://www.dlggzy.cn/jyxx/zfcg/zbjggs?currentPage={}&area=013&scrollValue=0', 121),
            # 工程建设 招标公告 共132页 变更通知 共90页 评标结果公示 共102页 中标结果公示 共146页 每天更新跨度均1页
            ('招标公告', 'https://www.dlggzy.cn/jyxx/jsgcZbgg?currentPage={}&area=013&scrollValue=0', 132),
            ('变更公告', 'https://www.dlggzy.cn/jyxx/jsgcBgtz?currentPage={}&area=013&scrollValue=0', 90),
            ('招标结果', 'https://www.dlggzy.cn/jyxx/jsgcpbjggs?currentPage={}&area=013&scrollValue=0', 102),
            ('招标结果', 'https://www.dlggzy.cn/jyxx/jsgcZbjggs?currentPage={}&area=013&scrollValue=0', 146),
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
        # 由于第一个并非是有效信息
        infos = response.xpath('//div[@class="news"]//tr')[1:]

        for each_li in infos:
            items['title'] = ''
            items['url'] = ''
            items['web_time'] = ''
            items['intro'] = ''
            items['addr_id'] = ''

            try:
                if 'jsgcBgtz' not in response.url and 'jsgcZbjggs' not in response.url:
                    items['title'] = each_li.xpath(self.xpath_rule['title_rule']).extract_first().strip()
                elif 'jsgcZbjggs' not in response.url:
                    items['title'] = each_li.xpath(self.xpath_rule['modify_title_rule']).extract_first().strip()
                else:
                    items['title'] = each_li.xpath(self.xpath_rule['result_title_rule']).extract_first().strip()
            except:
                pass

            try:
                if 'jsgcBgtz' not in response.url:
                    items['url'] = self.baseUrl + each_li.xpath(self.xpath_rule['url_rule']).extract_first()
                else:
                    items['url'] = self.baseUrl + each_li.xpath(self.xpath_rule['modify_url_rule']).extract_first()
            except:
                print(items)
                msg = self.name + ', 该爬虫详情页获取url失败'
                send_mail_when_error(msg)
                self.error_count += 1
                if self.error_count > 3:
                    quit()
                    msg = self.name + ', 该爬虫因详情页获取失败被暂停'
                    send_mail_when_error(msg)
                pass

            try:
                if 'jsgcBgtz' not in response.url:
                    items['web_time'] = each_li.xpath(self.xpath_rule['web_time_rule']).extract_first().strip()
                else:
                    items['web_time'] = each_li.xpath(self.xpath_rule['modify_web_time_rule']).extract_first().strip()
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

        if '更正' in items['title'] or '变更' in items['title']:
            items['type_id'] = '38256'

        items["source_name"] = self.source_name
        yield items