# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import time
import re
from utils.STMP import send_mail_when_error
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category

# http://www.msggzy.org.cn/front/ @ 眉山市公共资源交易网
class meishanSpiderSpider(scrapy.Spider):
    name = 'meishan_city_gov_spider'
    # allowed_domains = ['msggzy.org.cn']

    def __init__(self):

        self.city_dict = get_city_dict()
        self.regularExpression = regularExpression
        self.regularExpression02 = regularExpression02
        self.category = category

        self.govPurchase_baseUrl = 'http://www.msggzy.org.cn'

        self.error_count = 0

        self.start_urls = [
            # 采购公告
            # 政府采购公告 共5页 每天更新1页
            ('招标公告', 'http://www.msggzy.org.cn/front/zfcg/002001/?Paging={}', 3),
            # 政府采购变更公告 共3页 同上一页
            ('变更公告', 'http://www.msggzy.org.cn/front/zfcg/002002/?Paging={}', 3),
            # 政府采购结果 共6页 同上一页
            ('招标结果', 'http://www.msggzy.org.cn/front/zfcg/002003/?Paging={}', 3),
            # 工程建设
            # 工程建设招标公告 共17页 每天更新1页
            ('招标公告', 'http://www.msggzy.org.cn/front/jsgc/001002/?Paging={}', 3),
            # 中标候选人公示 共17页 每天更新跨度1页
            ('招标结果', 'http://www.msggzy.org.cn/front/jsgc/001013/?Paging={}', 3),
            # 工程建设招标结果  共16页 每天更新跨度1页
            ('招标结果', 'http://www.msggzy.org.cn/front/jsgc/001015/?Paging={}', 3),
        ]

        self.headers = {
            'Host': 'www.msggzy.org.cn',
        }

    def start_requests(self):
        for url_info in self.start_urls:
            urls = [url_info[1].format(i) for i in range(1, url_info[2])]
            for url in urls:
                items = {}
                items['type_id'] = self.category[url_info[0]]
                yield scrapy.Request(url, callback=self.parse, meta={"items": deepcopy(items)}, headers = self.headers)

    def parse(self, response):
        items = response.meta['items']
        # 由于最后一个tr标签为页数栏、所以排除掉
        all_trs = response.xpath('//div[@class="ewb-comp-bd"]//table//tr')[:-1]

        for each_tr in all_trs:
            items['title'] = ''
            items['url'] = ''
            items['web_time'] = ''
            items['intro'] = ''
            items['addr_id'] = ''

            try:
                items['title'] = each_tr.xpath('./td[1]/a/@title').extract_first()
            except:
                pass

            try:
                items['url'] = self.govPurchase_baseUrl + each_tr.xpath('./td[1]/a/@href').extract_first()
            except:
                msg = self.name + ', 该爬虫详情页获取url失败'
                send_mail_when_error(msg)
                self.error_count += 1
                if self.error_count > 3:
                    quit()
                    msg = self.name + ', 该爬虫因详情页获取失败被暂停'
                    send_mail_when_error(msg)
                pass

            try:
                items['web_time'] = each_tr.xpath('./td[2]/text()').extract_first().strip()
            except:
                pass

            yield scrapy.Request(url = items['url'], callback = self.parse_article, meta = {'items' : deepcopy(items)}, headers = self.headers)


    def parse_article(self, response):

        items = response.meta['items']

        try:
            dirty_article = re.search(r'<!--EpointContent-->(.*?)<tr id="trAttach" runat="server">', response.text, re.S).group(1)

            if items['type_id'] == '38255':
                dirty_article = re.sub(self.regularExpression02, '>', dirty_article)

            clean_article = re.sub(self.regularExpression, ' ', dirty_article)
            items['intro'] = clean_article
        except:
            pass

        items['addr_id'] = '426'
        items["source_name"] = '眉山市公共资源交易网'

        yield items