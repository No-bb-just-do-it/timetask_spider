# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
from utils.STMP import send_mail_when_error
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, category
from .common_spider import CommonSpider

# http://www.cjhdj.com.cn/xxgk/wsgs/zbgg/ @ 长江航道局
class changjiang_waterwaySpiderSpider(CommonSpider):
    name = 'changjiang_waterway_spider'
    allowed_domains = ['cjhdj.com.cn']

    def __init__(self):

        self.city_dict = get_city_dict()
        self.regularExpression = regularExpression
        self.category = category

        self.bidNotice_baseUrl = 'http://www.cjhdj.com.cn/xxgk/wsgs/zbgg'
        self.resultNotice_baseUrl = 'http://www.cjhdj.com.cn/xxgk/wsgs/zbjggs'

        self.xpath_rule = {
            'list_page': '//div[@class="gl_list1"]//ul/li',
            'title_rule': './h3//a/text()',
            'url_rule': './h3//a/@href',
            'web_time_rule': './h3/span/text()',
            'content_rule': r'<div class="bor1 pad_t20 mar_t15">(.*?)<div class="xl_icon"'
        }

        self.error_count = 0
        self.source_name = '长江航道局'
        self.addr_id = ''

        self.start_urls = [
            # 共75页 每天更新跨度1页
            ('招标公告', 'http://www.cjhdj.com.cn/xxgk/wsgs/zbgg/index_{}.shtml', 3),
            # 共52页 每天更新跨度1页
            ('招标结果', 'http://www.cjhdj.com.cn/xxgk/wsgs/zbjggs/index_{}.shtml', 3),
        ]

        self.headers = {
            'Host': 'www.cjhdj.com.cn',
            'Referer': 'http://www.cjhdj.com.cn/xxgk/wsgs/zbgg/index_1.shtml',
            'Connection': 'keep-alive'
        }

    def start_requests(self):
        for url_info in self.start_urls:
            # 构造分页列表 第二页为index_1 第三页为index_2以此类推
            urls = [url_info[1].format(i) for i in range(0, url_info[2])]
            for url in urls:
                if 'index_0' in url and 'zbgg' in url:
                    url = 'http://www.cjhdj.com.cn/xxgk/wsgs/zbgg/index.shtml'
                elif 'index_0' in url and 'zbjggs' in url:
                    url = 'http://www.cjhdj.com.cn/xxgk/wsgs/zbjggs/index.shtml'
                items = {}
                items["type_id"] = self.category[url_info[0]]
                yield scrapy.Request(url, callback=self.parse, meta={"items": deepcopy(items)}, headers = self.headers)

    def parse(self, response):
        items = response.meta['items']

        # 获取所有招标信息的li标签
        all_lis = response.xpath(self.xpath_rule['list_page'])

        for each_li in all_lis:
            items['title'] = ''
            items['url'] = ''
            items['web_time'] = ''
            items['intro'] = ''
            items['addr_id'] = ''

            try:
                items['title'] = each_li.xpath(self.xpath_rule['title_rule']).extract_first()
            except:
                pass

            try:
                if items['type_id'] == '38255':
                    items['url'] = self.bidNotice_baseUrl + each_li.xpath(self.xpath_rule['url_rule']).extract_first()[1:]
                else:
                    items['url'] = self.resultNotice_baseUrl + each_li.xpath(self.xpath_rule['url_rule']).extract_first()[1:]
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
                items['web_time'] = each_li.xpath(self.xpath_rule['web_time_rule']).extract_first()
            except:
                pass

            yield scrapy.Request(items['url'], callback = self.parse_article, headers = self.headers, meta = {'items' : deepcopy(items)})

