# -*- coding: utf-8 -*-
from .common_spider import CommonSpider
from utils.Regular_Expression import category

# http://www.jxzbtb.cn/jygg/003002/1.html @ 嘉兴市公共资源交易中心
class jiaxingSpiderSpider(CommonSpider):
    name = 'jiaxing_city_gov_spider'

    def __init__(self):

        self.baseUrl = 'http://www.jxzbtb.cn'
        self.error_count = 0
        self.source_name = '嘉兴市公共资源交易中心'
        self.addr_id = '401'
        self.category = category

        self.xpath_rule = {
            'list_page' : '//div[@class="ewb-con-bd"]/ul/li',
            'title_rule' : './div/a/@title',
            'url_rule' : './div/a/@href',
            'web_time_rule' : './/span/text()',
            'content_rule' : r'<p class="info-sources">.*?</p>(.*?)<!-- footer -->'
        }

        self.headers = {
            'Host': 'www.jxzbtb.cn',
            'Connection': 'keep-alive',
            'Referer': 'http://www.jxzbtb.cn/jygg/003002/261.html'
        }

        self.start_urls = [
            # 政府采购 262页 每天更新跨度1页
            ('招标公告', 'http://www.jxzbtb.cn/jygg/003001/{}.html', 3),
            # 建设工程 78页 每天更新跨度1页
            ('招标公告', 'http://www.jxzbtb.cn/jygg/003002/{}.html', 3),
        ]