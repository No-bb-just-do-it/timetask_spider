# -*- coding: utf-8 -*-
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category
from utils.parse_content import pc
from .common_spider import CommonSpider

# http://www.ggzy.anshun.gov.cn/jyxx/003002/003002001/1.html @ 安顺市全国公共资源交易平台
class anshunSpiderSpider(CommonSpider):
    name = 'anshun_city_gov_spider'

    def __init__(self):

        self.city_dict = get_city_dict()
        self.category = category

        self.baseUrl = 'http://www.ggzy.anshun.gov.cn'

        self.xpath_rule = {
            'list_page' : '//div[@class="ewb-right-bd"]/ul/li',
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