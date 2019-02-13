# -*- coding: utf-8 -*-
import re
from copy import deepcopy

from utils.STMP import send_mail_when_error
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category
from .common_spider import CommonSpider
import scrapy

# http://zhuzhou.hnsggzy.com/jygkzfcg/index_1.jhtml @ 株洲市公共资源交易网
class zhuzhouSpiderSpider(CommonSpider):
    name = 'zhuzhou_city_gov_spider'
    # allowed_domains = ['msggzy.org.cn']

    def __init__(self):

        self.city_dict = get_city_dict()
        self.regularExpression = regularExpression
        self.regularExpression02 = regularExpression02
        self.category = category

        self.govPurchase_baseUrl = 'http://www.dqgpc.gov.cn'

        self.error_count = 0
        self.source_name = '株洲市公共资源交易网'
        self.addr_id = '431'
        self.baseUrl = ''

        self.xpath_rule = {
            'list_page': '//div[@class="article-content"]/ul/li',
            'title_rule': './div[1]/a//text()',
            'url_rule': './div[1]/a/@href',
            'web_time_rule': './div[1]//div/text()',
            'content_rule': r'<div class="content">(.*?)<span><a href="'
        }

        self.start_urls = [
            # 政府采购类 包含采购公告、采购结果 共273页 每天更新1页
            ('招标公告', 'http://zhuzhou.hnsggzy.com/jygkzfcg/index_{}.jhtml', 3),
            # 工程建设类 包含公告、结果、  共200页 每天更新1页
            ('招标公告', 'http://zhuzhou.hnsggzy.com/gczb/index_{}.jhtml', 3),
        ]

        self.headers = {
            'Host': 'zhuzhou.hnsggzy.com',
            'Referer': 'http://zhuzhou.hnsggzy.com/jygkzfcg/index_2.jhtml'
        }