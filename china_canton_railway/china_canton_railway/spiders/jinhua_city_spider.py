# -*- coding: utf-8 -*-
import re
from copy import deepcopy
import scrapy
from .common_spider import CommonSpider
from utils.Regular_Expression import category, regularExpression02, regularExpression


# http://www.jhztb.gov.cn/jhztb/zfcgcggg/index_1.htm @ 金华市公共资源交易中心
class jinhuaSpiderSpider(CommonSpider):
    name = 'jinhua_city_gov_spider'

    def __init__(self):

        self.baseUrl = 'http://www.jhztb.gov.cn'
        self.error_count = 0
        self.source_name = '金华市公共资源交易中心'
        self.addr_id = '401'
        self.category = category

        self.xpath_rule = {
            'list_page' : '//div[@class="Right-Border floatL"]/dl/dt',
            'title_rule' : './/a/text()',
            'url_rule' : './/a/@href',
            'web_time_rule' : './/span//text()',
            'content_rule' : r"<img  class='Wzimg' src='(.*?)'"
        }

        self.headers = {
            'Host': 'www.jhztb.gov.cn',
            'Connection': 'keep-alive',
            # 'Referer': 'http://www.jxzbtb.cn/jygg/003002/261.html'
        }

        self.start_urls = [
            # 政府采购 采购公告134 采购结果公示29 中标成功公告124 每天更新跨度均1页
            # ('招标公告', 'http://www.jhztb.gov.cn/jhztb/zfcgcggg/index_{}.htm', 3),
            # ('招标结果', 'http://www.jhztb.gov.cn/jhztb/zfcgzbgg/index_{}.htm', 3),
            # ('招标结果', 'http://www.jhztb.gov.cn/jhztb/zfcgzbhxgs/index_{}.htm', 3),
            # 省重点工程建设 招标公告6页 中标公示5页 均1页 定时任务写死一页即可
            # ('招标公告', 'http://www.jhztb.gov.cn/jhztb/gcjyysgs/index_{}.htm', 3),
            # ('招标结果', 'http://www.jhztb.gov.cn/jhztb/gcjyzbzy/index_{}.htm', 3),
            # 金华山工程 招标公告41页 中标公示32页 均1页 定时任务写死一页即可
            # ('招标公告', 'http://www.jhztb.gov.cn/jhztb/jsgcgcjszbgg/index_{}.htm', 3),
            # ('招标结果', 'http://www.jhztb.gov.cn/jhztb/jsgcgcjszbjg/index_{}.htm', 3),
            # 市本级工程 招标公告6页 中标公示2页 均1页 定时任务写死一页即可
            ('招标公告', 'http://www.jhztb.gov.cn/jhztb/jsgcjhszbgg/index_{}.htm', 3),
            ('招标结果', 'http://www.jhztb.gov.cn/jhztb/jsgcjhszbjg/index_{}.htm', 3),
        ]

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
                dirty_title = ''.join(each_li.xpath(self.xpath_rule['title_rule']).extract()).strip()
                try:
                    items['title'] = dirty_title.split(']')[-1]
                except:
                    items['title'] = dirty_title
            except:
                pass

            try:
                items['url'] = self.baseUrl + each_li.xpath(self.xpath_rule['url_rule']).extract_first()
                if items['url'] == None:
                    raise Exception
            except:
                msg = self.name + ', 该爬虫详情页获取url失败'
                # send_mail_when_error(msg)
                self.error_count += 1
                if self.error_count > 3:
                    quit()
                    msg = self.name + ', 该爬虫因详情页获取失败被暂停'
                    # send_mail_when_error(msg)
                pass

            try:
                dirty_web_time = each_li.xpath(self.xpath_rule['web_time_rule']).extract_first()
                items['web_time'] = re.sub(r'\[|\]', '', dirty_web_time)
            except:
                pass
            yield scrapy.Request(items['url'], callback = self.parse_article, headers = self.headers, meta = {'items' : deepcopy(items)})


    def parse_article(self, response):
        items = response.meta['items']
        try:
            pic_url = re.search(self.xpath_rule['content_rule'], response.text, re.S).group(1)
            clean_article = '<img src="{}">'.format(pic_url)
            items['intro'] = clean_article
        except:
            pass

        if 'img' not in items['intro']:
            try:
                dirty_article = re.search(r'<div class="content-Border floatL">(.*?)<td>上一条', response.text, re.S).group(1)
                dirty_article = re.sub(regularExpression02, '>', dirty_article)
                clean_article = re.sub(regularExpression, ' ', dirty_article)
                items['intro'] = clean_article
            except:
                pass

        if '中标' in items['title'] or '成交' in items['title'] or '结果' in items['title']:
            items['type_id'] = '38257'
        elif '更正' in items['title'] or '变更' in items['title']:
            items['type_id'] = '38256'

        items['addr_id'] = self.addr_id
        items["source_name"] = self.source_name
        yield items
