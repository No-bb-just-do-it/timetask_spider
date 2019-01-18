# -*- coding: utf-8 -*-
# http://e.sinochemitc.com/cms/channel/ywgg1qb/index.htm@中化
import re
import time
from copy import deepcopy
from STMP import send_mail_when_error
from scrapy.exceptions import CloseSpider
import scrapy


class SinochemSpiderSpider(scrapy.Spider):
    name = 'sinochem_spider'
    allowed_domains = ['sinochemitc.com']
    start_urls = ['http://sinochemitc.com/']

    def __init__(self):
        # 文章拼接url
        self.base_url = 'http://e.sinochemitc.com/'

        self.city_dict = {}
        # 将各个城市与编号制成字典
        with open('城市编号id.txt', 'r', encoding='GB2312')as f:
            city_data = f.read()
            for each_info in city_data.split('\n'):
                self.city_dict[each_info.split(',')[0]] = each_info.split(',')[1]

        self.pattern01 = r'址：(.{200})'
        self.pattern_list = [self.pattern01]

        self.category = {
            '招标公告' : '38255',
            '招标结果' : '38257'
        }

        self.start_urls = [
            # 招标、预审、更正公告 共157页 每天更新跨度1页
            ('招标公告', "http://e.sinochemitc.com/cms/channel/ywgg1qb/index.htm?pageNo={}", 3),
            # 中标结果 共90页 每天更新跨度1页
            ('招标结果', "http://e.sinochemitc.com/cms/channel/ywgg2qb/index.htm?pageNo={}", 3),
            # 非招标采购公告 共11页 每天更新跨度1页
            ('招标公告', "http://e.sinochemitc.com/cms/channel/ywgg3qb/index.htm?pageNo={}", 3),

        ]

        self.error_count = 0

        with open('/root/RegularExpression.txt', 'r')as f:
            self.regularExpression = f.read()

    def quit(self):
        raise CloseSpider('close spider')

    def start_requests(self):
        for url_info in self.start_urls:
            # 构造分页列表
            urls = [url_info[1].format(i) for i in range(1, url_info[2])]
            for url in urls:
                items = {}
                items["type_id"] = self.category[url_info[0]]
                yield scrapy.Request(url, callback=self.parse, meta={"items": deepcopy(items)}, dont_filter = True)


    def parse(self, response):
        items = response.meta['items']

        all_lis = response.xpath('//div[@id="tab1"]/ul/li')

        for each_li in all_lis[:]:

            items['title'] = ''
            items['url'] = ''
            items['web_time'] = ''
            items['intro'] = ''
            items['addr_id'] = ''

            try:
                items['title'] = each_li.xpath('./a/@title').extract_first()
            except:
                pass
            else:
                if '更正' in items['title'] or '变更' in items['title']:
                    items['type_id'] = '38256'

            try:
                items['url'] = self.base_url + each_li.xpath('./a/@href').extract_first()
            except:
                msg = self.name + ', 该爬虫详情页获取url失败'
                send_mail_when_error(msg)
                self.error_count += 1
                if self.error_count > 3:
                    self.quit()
                    msg = self.name + ', 该爬虫因详情页获取失败被暂停'
                    send_mail_when_error(msg)
                pass

            try:
                items['web_time'] = each_li.xpath('.//p[@class="time"]/text()').extract_first().split('： ')[1].strip()
            except:
                pass

            yield scrapy.Request(url = items['url'], callback = self.parse_article, meta = {'items' : deepcopy(items)})

    def parse_article(self, response):
        items = response.meta['items']

        try:
            dirty_article = re.search(r'<div class="ninfo-title">(.*?)<!-- 附件 -->', response.text, re.S).group(1)
            # clean_article = re.sub(
            #     r'\r|\t|\n|<!--.*?-->|<input.*?>|class=[\'\"].*?[\'\"]|id=[\'\"].*?[\'\"]|style=[\'\"].*?[\'\"]|<STYLE.*?>.*?<\/STYLE>|class=\w*',
            #     ' ', dirty_article)
            # 将文章的垃圾数据进行清洗（服务器版）
            clean_article = re.sub(eval(self.regularExpression), ' ', dirty_article)
        except:
            pass
        else:
            items['intro'] = clean_article

        for city in self.city_dict:
            if city in items['title']:
                items['addr_id'] = self.city_dict[city]
                break

        # 因为根据标题获取地名有时候会获取不到、所以再进行多一层判断从正文中获取地市名
        if items['addr_id'] == '':
            for each_pattern in self.pattern_list:
                try:
                    search_text = re.search(each_pattern, dirty_article, re.S).group(1)
                except:
                    continue
                else:
                    for city_name in self.city_dict:
                        if city_name in search_text:
                            items['addr_id'] = self.city_dict[city_name]
                            break
                if 'addr_id' in items:
                    break

        if items['addr_id'] == '':
            items['addr_id'] = '100'

        # 系统时间，时间戳
        items["time"] = '%.0f' % time.time()
        # 分类id
        items["sheet_id"] = '29'
        # 文章来源
        items["source_name"] = '中化商务电子招投标平台'

        yield items


