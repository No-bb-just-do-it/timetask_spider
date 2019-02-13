# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category
import re
from utils.STMP import send_mail_when_error
from utils.parse_content import pc
from .common_spider import CommonSpider

# http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006002/006002001/ @ 荆州市公共资源交易信息网
class jingzhouSpiderSpider(CommonSpider):
    name = 'jingzhou_city_gov_spider'

    def __init__(self):

        self.city_dict = get_city_dict()
        self.category = category

        self.baseUrl = 'http://www.jzggzy.com'

        self.xpath_rule = {
            'list_page' : '//div[@class="con-list"]/table//tr[@height="24"]',
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