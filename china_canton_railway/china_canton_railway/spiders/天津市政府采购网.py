# -*- coding: utf-8 -*-
import re
from copy import deepcopy
import scrapy
from utils.STMP import send_mail_when_error
from .common_spider import CommonSpider
from utils.Regular_Expression import category, regularExpression02, regularExpression


# http://www.tjgp.gov.cn/portal/topicView.do?method=view&view=Infor&id=1664&ver=2&stmp=1550470572396 @ 天津市政府采购网
class tianjinSpiderSpider(CommonSpider):
    name = 'tianjin_city_gov_spider'

    def __init__(self):

        self.baseUrl = 'http://www.tjgp.gov.cn'
        self.error_count = 0
        self.source_name = '天津市政府采购网'
        self.addr_id = '408'
        self.category = category

        self.date_keys = {'Jan': '1', 'Feb': '2', 'Mar': '3', 'Apr': '4', 'May': '5', 'Jun': '6', 'Jul': '7',
                          'Aug': '8', 'Sep': '9', 'Oct': '10', 'Nov': '11', 'Dec': '12'}

        self.xpath_rule = {
            'list_page' : '//div[@id="reflshPage"]/ul/li',
            'title_rule' : './/a/@title',
            'url_rule' : './/a/@href',
            'web_time_rule' : './/span/text()',
            'content_rule' : r'<tbody>(.*?)</body>'
        }

        self.headers = {
            'Host': 'www.tjgp.gov.cn',
            'Connection': 'keep-alive',
            'Referer': 'http://www.tjgp.gov.cn/portal/topicView.do?method=view&view=Infor&id=1664&ver=2&stmp=1550470572396'
        }

        self.start_urls = [
            # 市级采购公告 1803 更新跨度2页
            ('招标公告', 'http://www.tjgp.gov.cn/portal/topicView.do?method=view&page={}&id=1665&step=1&view=Infor&st=1', 3),
            # 区级采购公告 1803 更新跨度2页
            ('招标公告', 'http://www.tjgp.gov.cn/portal/topicView.do?method=view&page={}&id=1664&step=1&view=Infor', 3),
            # 市级更正公告 404 更新跨度1页
            ('变更公告', 'http://www.tjgp.gov.cn/portal/topicView.do?method=view&page={}&id=1663&step=1&view=Infor', 3),
            # 区级更正公告 586 更新跨度1页
            ('变更公告', 'http://www.tjgp.gov.cn/portal/topicView.do?method=view&page={}&id=1666&step=1&view=Infor', 3),
            # 市级采购结果 2061 更新跨度2页
            ('招标结果', 'http://www.tjgp.gov.cn/portal/topicView.do?method=view&page={}&id=2014&step=1&view=Infor&st=1', 3),
            # 市级采购结果 2762 更新跨度2页
            ('招标结果', 'http://www.tjgp.gov.cn/portal/topicView.do?method=view&page={}&id=2013&step=1&view=Infor&st=1', 3),
            # 市级单一来源 229 更新跨度2页
            ('招标公告', 'http://www.tjgp.gov.cn/portal/topicView.do?method=view&page={}&id=2033&step=1&view=Infor&st=1', 3),
            # 区级单一来源 164 更新跨度2页
            ('招标公告', 'http://www.tjgp.gov.cn/portal/topicView.do?method=view&page={}&id=2034&step=1&view=Infor&st=1', 3),

        ]

    def switch_date(self, page_date):
        date = page_date.split(' ')
        year = date[-1]
        month = self.date_keys[date[1]]
        day = date[2]
        return year + '-' + month + '-' + day

    def parse(self, response):
        items = response.meta['items']

        infos = response.xpath(self.xpath_rule['list_page'])

        for each_li in infos:
            items['title'] = ''
            items['url'] = ''
            items['web_time'] = ''
            items['intro'] = ''
            items['addr_id'] = ''

            try:
                items['title'] = ''.join(each_li.xpath(self.xpath_rule['title_rule']).extract()).strip()
            except:
                pass

            try:
                items['url'] = self.baseUrl + each_li.xpath(self.xpath_rule['url_rule']).extract_first()
                if items['url'] == None:
                    raise Exception
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
                page_date = each_li.xpath(self.xpath_rule['web_time_rule']).extract_first().strip()
                items['web_time'] = self.switch_date(page_date)
            except:
                pass
            yield scrapy.Request(items['url'], callback=self.parse_article, headers=self.headers,
                                 meta={'items': deepcopy(items)})

    def parse_article(self, response):
        items = response.meta['items']
        try:
            dirty_article = re.search(self.xpath_rule['content_rule'], response.text, re.S).group(1)
            # dirty_article = re.sub('&#.*?;', '', dirty_article)
            dirty_article = re.sub(regularExpression02, '>', dirty_article)
            clean_article = re.sub(regularExpression, ' ', dirty_article)
            items['intro'] = clean_article
        except:
            pass

        items['addr_id'] = self.addr_id
        items["source_name"] = self.source_name
        yield items