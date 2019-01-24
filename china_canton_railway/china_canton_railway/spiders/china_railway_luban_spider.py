# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import time
import re
from utils.STMP import send_mail_when_error
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, category

# http://www.crecgec.com/forum.php?mod=forumdisplay&fid=2&filter=sortid&sortid=12@中铁鲁班商务
class ChinaRailwayLubanSpiderSpider(scrapy.Spider):
    name = 'china_railway_luban_spider'
    allowed_domains = ['crecgec.com']

    def __init__(self):
        self.headers = {
                'Host': 'www.crecgec.com',
                'Connection': 'keep-alive',
}
        # 获取城市字典
        self.city_dict = get_city_dict()
        # 获取招标信息种类
        self.category = category
        # 获取正则规则
        self.regularExpression = regularExpression
        self.error_count = 0

        # 文章拼接的url
        self.article_url = 'http://www.crecgec.com/'

        self.start_urls = [
            # 采购公告 共995页 每天更新跨度4页
            ('招标公告', "http://www.crecgec.com/forum.php?mod=forumdisplay&fid=2&sortid=12&filter=sortid&sortid=12&mcode=0001&page={}", 3),
            # 竞争性谈判 共504页 每天更新跨度3页
            ('招标公告', "http://www.crecgec.com/forum.php?mod=forumdisplay&fid=2&sortid=14&filter=sortid&sortid=14&page={}", 3),
            # 结果公示 共1000页 每天更新跨度3页
            ('变更公告', "http://www.crecgec.com/forum.php?mod=forumdisplay&fid=2&sortid=13&sortid=13&filter=sortid&page={}", 3),
        ]

    def start_requests(self):
        for url_info in self.start_urls:
            start_urls = [url_info[1].format(page) for page in range(1, url_info[2])]
            for each_url in start_urls:
                items = {}
                items['type_id'] = self.category[url_info[0]]
                yield scrapy.Request(url = each_url, callback = self.parse, meta = {'items' : deepcopy(items)}, headers = self.headers)

    def parse(self, response):
        items = response.meta['items']
        # 获取所有招标信息的li标签
        all_lis = response.xpath('//form[@id="moderate"]/li')

        for each_li in all_lis:

            items['title'] = ''
            items['url'] = ''
            items['web_time'] = ''
            items['intro'] = ''
            items['addr_id'] = ''

            try:
                items['title'] = each_li.xpath('./a/span/text()').extract_first().strip()
            except:
                pass

            try:
                items['url'] = self.article_url + each_li.xpath('./a/@href').extract_first()
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
                items['web_time'] = each_li.xpath('.//em/text()').extract_first().split(' ')[0].strip()
            except:
                pass

            for city in self.city_dict:
                if city in items['title']:
                    items['addr_id'] = self.city_dict[city]
                    break

            yield scrapy.Request(url = items['url'], callback = self.article_parse, meta = {'items' : deepcopy(items)})


    def article_parse(self, response):
        items = response.meta['items']

        try:
            dirty_article = re.search(r'<div class="details">(.*?)<div class="tishiB">', response.text, re.S).group(1)
            # 垃圾清洗
            clean_article = re.sub(self.regularExpression, ' ', dirty_article)
            items['intro'] = clean_article

        except Exception as e:
            print('文章提取出错原因 : ', e)
            pass

        # 文章来源
        items["source_name"] = '中国中铁采购电子商务平台'

        yield items