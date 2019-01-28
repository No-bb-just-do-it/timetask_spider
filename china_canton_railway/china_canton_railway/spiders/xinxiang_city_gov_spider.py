# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category
import re
from utils.STMP import send_mail_when_error
from utils.parse_content import pc

# http://xinxiang.hngp.gov.cn/xinxiang/ggcx?appCode=H68&channelCode=0101&bz=0&pageSize=20&pageNo=1 @ 新乡市政府采购网
class xinxiangSpiderSpider(scrapy.Spider):
    name = 'xinxiang_city_gov_spider'

    def __init__(self):

        self.city_dict = get_city_dict()
        self.category = category

        self.baseUrl = 'http://xinxiang.hngp.gov.cn'

        self.xpath_rule = {
            'title_rule': './a/text()',
            'url_rule': './a/@href',
            'web_time_rule': './span/text()',
            'content_rule' : r'</P>(.*?)<!--EndFragment-->'
        }

        self.error_count = 0
        self.source_name = '新乡市政府采购网'

        self.regularExpression = regularExpression
        self.regularExpression02 = regularExpression02

        self.addr_id = '429'

        self.headers = {
            'Host': 'xinxiang.hngp.gov.cn',
            'Referer': 'http://xinxiang.hngp.gov.cn/xinxiang/content?infoId=1548325966768822&channelCode=H680201&bz=0'
        }

        self.pc = pc

        self.bidNotice_url = 'http://xinxiang.hngp.gov.cn/webfile/xinxiang/cgxx/cggg/webinfo/{}/{}/{}.htm'
        self.bidResult_url = 'http://xinxiang.hngp.gov.cn/webfile/xinxiang/cgxx/jggg/webinfo/{}/{}/{}.htm'
        self.modifyResult_url = 'http://xinxiang.hngp.gov.cn/webfile/xinxiang/cgxx/bggg/webinfo/{}/{}/{}.htm'

        self.start_urls = {
            # 采购公告 共1305页 每天更新跨度1页 但只能爬前200页
            ('招标公告', 'http://xinxiang.hngp.gov.cn/xinxiang/ggcx?appCode=H68&channelCode=0101&bz=0&pageSize=20&pageNo={}', 3),
            ('招标结果', 'http://xinxiang.hngp.gov.cn/xinxiang/ggcx?appCode=H68&channelCode=0102&bz=0&pageSize=20&pageNo={}', 3),
            ('变更公告', 'http://xinxiang.hngp.gov.cn/xinxiang/ggcx?appCode=H68&channelCode=0103&bz=0&pageSize=20&pageNo={}', 3)
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

        infos = response.xpath('//div[@class="List2"]/ul/li')

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
                items['url'] = self.baseUrl + each_li.xpath(self.xpath_rule['url_rule']).extract_first()
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
                items['web_time'] = each_li.xpath(self.xpath_rule['web_time_rule']).extract_first().strip()
            except:
                pass

            # 分别需要使用年份月份id来构造真实文章的url链接
            year, month = items['web_time'].split('-')[0], items['web_time'].split('-')[1]
            article_id = re.search(r'infoId=(.*?)&', items['url'], re.S).group(1)

            if items['type_id'] == '38255':
                article_url = self.bidNotice_url.format(year, month, article_id)
            elif items['type_id'] == '38257':
                article_url = self.bidResult_url.format(year, month, article_id)
            else:
                article_url = self.modifyResult_url.format(year, month, article_id)

            yield scrapy.Request(article_url, callback = self.parse_article, headers = self.headers, meta = {'items' : deepcopy(items)})


    def parse_article(self, response):
        items = response.meta['items']

        try:
            items['intro'] = self.pc.get_clean_content(self.xpath_rule['content_rule'], self.regularExpression, self.regularExpression02, response.text)
        except:
            dirty_article = re.sub(self.regularExpression02, '>', response.text)
            clean_article = re.sub(self.regularExpression, ' ', dirty_article)
            items['intro'] = clean_article

        items['addr_id'] = self.addr_id

        if items['addr_id'] == '':
            for city in self.city_dict:
                if city in items['title']:
                    items['addr_id'] = self.city_dict[city]
                    break

        items["source_name"] = self.source_name
        yield items