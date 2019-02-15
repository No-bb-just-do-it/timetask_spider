# -*- coding: utf-8 -*-
from .common_spider import CommonSpider
from utils.Regular_Expression import category

# http://fzsggzyjyfwzx.cn/jyxxgcjs/index_1.jhtml @ 福州市公共资源交易网
class fuzhouSpiderSpider(CommonSpider):
    name = 'fuzhou_city_gov_spider'

    def __init__(self):

        self.baseUrl = 'http://fzsggzyjyfwzx.cn'
        self.error_count = 0
        self.source_name = '福州市公共资源交易网'
        self.addr_id = '403'
        self.category = category

        self.xpath_rule = {
            'list_page' : '//div[@class="article-content"]/ul/li',
            'title_rule' : './div/a//text()',
            'url_rule' : './div/a/@href',
            'web_time_rule' : './div/div/text()',
            'content_rule' : r'id="content">(.*?)<!--效果html开始-->'
        }

        self.headers = {
            'Host': 'fzsggzyjyfwzx.cn',
            'Connection': 'keep-alive',
            'Referer': 'http://fzsggzyjyfwzx.cn/jyxxgcjs/index_1.jhtml'
        }

        self.start_urls = [
            # 工程建设 175页 跨度共2页
            # ('招标公告', 'http://fzsggzyjyfwzx.cn/jyxxgcjs/index_1.jhtml', 3),
            # 政府采购 1045页 跨度共5页
            ('招标公告', 'http://fzsggzyjyfwzx.cn/jyxxzfcg/index_1.jhtml', 3)
        ]