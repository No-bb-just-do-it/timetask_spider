# -*- coding: utf-8 -*-
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category
from utils.parse_content import pc
from .common_spider import CommonSpider

# http://www.jztb.gov.cn/jyxx/077001/077001001/1.html @ 锦州市公共资源交易管理办公室
class yulinSpiderSpider(CommonSpider):
    name = 'yulin_city_gov_spider'

    def __init__(self):

        self.city_dict = get_city_dict()
        self.category = category

        self.baseUrl = 'http://www.yulin.gov.cn'

        self.xpath_rule = {
            'list_page' : '//div[@class="zfdtxx_lb bszn"]/ul/li',
            'title_rule': './/a/@title',
            'url_rule': './/a/@href',
            'web_time_rule': './span/text()',
            'content_rule' : r'</h3>(.*?)<a class="button"'
        }

        self.error_count = 0
        self.source_name = '玉林市人民政府门户网站'

        self.regularExpression = regularExpression
        self.regularExpression02 = regularExpression02

        self.addr_id = '416'

        self.headers = {
            'Host': 'www.yulin.gov.cn',
            'Referer': 'http://www.yulin.gov.cn/menhuwangzhan/zwgk/ggzypzlygk/zfcg/zbgg'
        }

        self.pc = pc

        self.start_urls = [
            # 招标公告2480 中标公告2247 变更公告185 单一来源11 废标公告111 每天更新量均1页
            ('招标公告', 'http://www.yulin.gov.cn/web/ylmh/channel/channel.ptl?pageNo={}&channelCode=001083032002002&$$time$$=20190213104940', 3),
            ('招标结果', 'http://www.yulin.gov.cn/web/ylmh/channel/channel.ptl?pageNo={}&channelCode=001083032002004&$$time$$=20190213134259', 3),
            ('变更公告', 'http://www.yulin.gov.cn/web/ylmh/channel/channel.ptl?pageNo={}&channelCode=001083032002003&$$time$$=20190213134346', 3),
            ('招标公告', 'http://www.yulin.gov.cn/web/ylmh/channel/channel.ptl?pageNo={}&channelCode=001083032002005&$$time$$=20190213134541', 3),
            ('招标结果', 'http://www.yulin.gov.cn/web/ylmh/channel/channel.ptl?pageNo={}&channelCode=001083032002006&$$time$$=20190213134841', 3),
        ]

