# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category
import re
from utils.STMP import send_mail_when_error
from utils.parse_content import pc
from utils.encode_url import aes

# http://ggzy.gzlps.gov.cn/jyxxzc/index_1.jhtml @ 六盘水市公共资源交易网
class liupanshuiSpiderSpider(scrapy.Spider):
    name = 'liupanshui_city_gov_spider'

    def __init__(self):

        self.city_dict = get_city_dict()
        self.category = category

        self.baseUrl = ''

        self.xpath_rule = {
            'title_rule': './p[1]/a/text()',
            'url_rule': './p[1]/a/@href',
            'web_time_rule': './p[2]/text()',
            'content_rule' : r'<div class="article">(.*?)<div class="footer">'
        }

        self.error_count = 0
        self.source_name = '六盘水市公共资源交易网'

        self.regularExpression = regularExpression
        self.regularExpression02 = regularExpression02

        self.addr_id = '425'

        self.headers = {
            'Host': 'ggzy.gzlps.gov.cn',
            'Referer': 'http://ggzy.gzlps.gov.cn/jyxxzc/index.jhtml'
        }

        self.pc = pc

        self.start_urls = [
            # 政府采购 共252页 每天更新跨度 1页
            ('招标公告', 'http://ggzy.gzlps.gov.cn/jyxxzc/index_{}.jhtml', 252),
            # 建设工程 共625页 每天更新跨度1页
            ('招标公告', 'http://ggzy.gzlps.gov.cn/jyxxgc/index_{}.jhtml', 625),
        ]


    def start_requests(self):
        for url_info in self.start_urls:
            urls = [url_info[1].format(i) for i in range(1, url_info[2])]
            for url in urls:
                items = {}
                items['type_id'] = self.category[url_info[0]]
                yield scrapy.Request(url, callback=self.parse, meta={"items": deepcopy(items)}, headers = self.headers)

    def parse(self, response):
        items = response.meta['items']

        infos = response.xpath('//ul[@class="erul"]/li')

        for each_li in infos:
            items['title'] = ''
            items['url'] = ''
            items['web_time'] = ''
            items['intro'] = ''
            items['addr_id'] = ''

            try:
                items['title'] = each_li.xpath(self.xpath_rule['title_rule']).extract_first().strip()
            except:
                pass

            try:
                get_url = self.baseUrl + each_li.xpath(self.xpath_rule['url_rule']).extract_first()
                get_prefix = re.search(r'(http://ggzy.gzlps.gov.cn:80/jyxx.*?/)', get_url, re.S).group(1)
                dirty_url = aes.url_encrypt(get_url)
                suffix_url = re.search(r'http://ggzy.gzlps.gov.cn:80/jyxx.*?/(.*)', dirty_url, re.S).group(1)
                if '/' in suffix_url:
                    items['url'] = get_prefix + suffix_url.replace('/', '%5E')
                else:
                    items['url'] = dirty_url
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
                items['web_time'] = re.sub('\.', '-', each_li.xpath(self.xpath_rule['web_time_rule']).extract_first().strip())
            except:
                pass

            yield scrapy.Request(items['url'], callback = self.parse_article, headers = self.headers, meta = {'items' : deepcopy(items)})


    def parse_article(self, response):
        items = response.meta['items']
        try:
            items['intro'] = self.pc.get_clean_content(self.xpath_rule['content_rule'], self.regularExpression, self.regularExpression02, response.text)
        except:
            pass

        items['addr_id'] = self.addr_id

        if items['addr_id'] == '':
            for city in self.city_dict:
                if city in items['title']:
                    items['addr_id'] = self.city_dict[city]
                    break

        if '废标' in items['title'] or '中标' in items['title'] or '成交' in items['title'] or '失败' in items['title']:
            items['type_id'] = '38257'
        elif '更正' in items['title'] or '变更' in items['title']:
            items['type_id'] = '38256'

        items["source_name"] = self.source_name
        yield items
