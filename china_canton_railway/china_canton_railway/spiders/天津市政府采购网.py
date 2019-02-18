# -*- coding: utf-8 -*-
from .common_spider import CommonSpider
from utils.Regular_Expression import category

# http://zfcg.yangzhou.gov.cn/ @ 扬州市政府采购网
class yangzhouSpiderSpider(CommonSpider):
    name = 'yangzhou_city_gov_spider'

    def __init__(self):

        self.baseUrl = ''
        self.error_count = 0
        self.source_name = '扬州市政府采购网'
        self.addr_id = '400'
        self.category = category

        self.xpath_rule = {
            'list_page' : '//div[@class="cont mt10"]/ul/li',
            'title_rule' : './/a/text()',
            'url_rule' : './/a/@href',
            'web_time_rule' : './/span/text()',
            'content_rule' : r'<div class="content" id="zoom">(.*?)<!-- bottom begin-->'
        }

        self.headers = {
            'Host': 'zfcg.yangzhou.gov.cn',
            'Connection': 'keep-alive'
        }