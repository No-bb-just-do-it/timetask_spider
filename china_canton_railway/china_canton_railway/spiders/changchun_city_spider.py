# -*- coding: utf-8 -*-
from copy import deepcopy

import scrapy

from .common_spider import CommonSpider
from utils.Regular_Expression import category
import json

# http://www.ccggzy.gov.cn/sjxxgk/002001/CityZfcgNotice.html @ 长春市公共资源交易网
class changchunSpiderSpider(CommonSpider):
    name = 'changchun_city_gov_spider'

    def __init__(self):

        self.baseUrl = 'http://www.ccggzy.gov.cn'
        self.error_count = 0
        self.source_name = '长春市公共资源交易网'
        self.addr_id = '412'
        self.category = category

        self.xpath_rule = {
            # 'list_page' : '//div[@class="cont mt10"]/ul/li',
            # 'title_rule': './/a/text()',
            # 'url_rule': './/a/@href',
            # 'web_time_rule': './/span/text()',
            'content_rule' : r'<!-- 正文 -->(.*?)<div class="ewb-text-content hidden'
        }

        self.headers = {
            'Host': 'www.ccggzy.gov.cn',
            'Connection': 'keep-alive',
            'Referer': 'http://www.ccggzy.gov.cn/sjxxgk/002001/CityZfcgNotice.html'
        }

        self.start_urls = [
            # 政府采购 全部分类共190页 每天更新一页
            ('招标公告', 'http://www.ccggzy.gov.cn/ccggzy/getxxgkAction.action?cmd=getCityZfcgInfo&pageIndex={}&pageSize=16&siteGuid=7eb5f7f1-9041-43ad-8e13-8fcb82ea831a&categorynum=002001&xiaqucode=220101&jyfl=%E5%85%A8%E9%83%A8', 3),
            # 政府采购 全部分类共536页 每天更新一页
            ('招标公告', 'http://www.ccggzy.gov.cn/ccggzy/getxxgkAction.action?cmd=getCityTradeInfo&pageIndex={}&pageSize=18&siteGuid=7eb5f7f1-9041-43ad-8e13-8fcb82ea831a&categorynum=002002&xiaqucode=220101', 3),
        ]

    def parse(self, response):
        items = response.meta['items']

        infos = json.loads(json.loads(response.text)['custom'])['Table']
        for each_li in infos:
            items['title'] = ''
            items['url'] = ''
            items['web_time'] = ''
            items['intro'] = ''
            items['addr_id'] = ''

            try:
                items['title'] = each_li['title'].strip()
            except:
                pass

            try:
                items['url'] = self.baseUrl + each_li['href']
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
                items['web_time'] = each_li['infodate'].strip()
            except:
                pass
            yield scrapy.Request(items['url'], callback = self.parse_article, headers = self.headers, meta = {'items' : deepcopy(items)})