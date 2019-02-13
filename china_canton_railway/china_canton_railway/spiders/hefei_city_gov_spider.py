# -*- coding: utf-8 -*-
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category
from utils.parse_content import pc
from .common_spider import CommonSpider

# http://zwgk.hefei.gov.cn/zwgk/public/index.xp?doAction=zdlylist2&type=5&id=001000180002&curPage=1 @ 合肥市政府信息公开网
class hefeiSpiderSpider(CommonSpider):
    name = 'hefei_city_gov_spider'

    def __init__(self):

        self.city_dict = get_city_dict()
        self.category = category

        self.baseUrl = 'http://zwgk.hefei.gov.cn'

        self.xpath_rule = {
            'list_page' : '//form[@name="form1"]/table/tr[3]//table',
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