# -*- coding: utf-8 -*-
# prcmNotices 采购公告  152页
# dealNotices 中标(成交)公告  540页
# invalidNotices 废标公告  18页
# modfiyNotices 更正公告 28页
# endNotices 终止公告 5页
# 来源 ：http://www.ccgp-hunan.gov.cn/page/notice/more.jsp#
import json
import re
from copy import deepcopy
import scrapy
import time
from datetime import datetime, date, timedelta


class HunanProvinceAnnounceSpider(scrapy.Spider):
    name = 'hunan_province_announce'
    allowed_domains = ['ccgp-hunan.gov.cn']
    # start_urls = ['http://ccgp-hunan.gov.cn/']

    def __init__(self):
        # 该url用来拼接文章url，用于items['url']字段  获取文章文本的url或许不是这个
        self.article_url = 'http://www.ccgp-hunan.gov.cn/page/notice/notice.jsp?noticeId={}'
        # 文章的真实地址
        self.origin_text_url = 'http://www.ccgp-hunan.gov.cn/mvc/viewNoticeContent.do?noticeId={}&area_id='
        # 文章列表页链接(需要用post请求)
        self.article_list_interface = 'http://www.ccgp-hunan.gov.cn/mvc/getNoticeList4Web.do'
        # 获取当天日期
        self.today = str(date.today())
        self.category = {
            '成交公告' : '38257', '采购公告' : '38255', '合同公告' : '38255', '单一来源公示' : '38255', '更正公告' : '38256'
        }

        with open('/root/RegularExpression.txt', 'r')as f:
            self.regularExpression = f.read()

    def start_requests(self):
        # 采购公告 共1820页 每天数据跨度40页左右
        for page in range(1, 51):
            # post请求的表单数据
            data = {
                'pType': '',
                'prcmPrjName': '',
                'prcmItemCode': '',
                'prcmOrgName': '',
                'startDate': '2019-01-01',
                'endDate': self.today,
                'prcmPlanNo': '',
                'page': str(page),
                'pageSize': '18'
            }

            yield scrapy.FormRequest(
                    url = self.article_list_interface,
                    formdata = data,
                    callback = self.parse,
                    dont_filter = True
            )

    # 解析文章列表
    def parse(self, response):
        try:
            # 文章列表页的json源代码
            json_article_list = response.text
            resp = json.loads(json_article_list)

            for each_article in resp['rows']:
                items = {}
                items['title'] = each_article['NOTICE_TITLE'].strip()
                items['web_time'] = each_article['NEWWORK_DATE']
                items['url'] = self.article_url.format(str(each_article['NOTICE_ID']))
                items['category'] = each_article['NOTICE_NAME']
                items['type_id'] = self.category[items['category']]
                # 文章真实链接
                article_text_url = self.origin_text_url.format(each_article['NOTICE_ID'])
                yield scrapy.Request(article_text_url, callback=self.parse_article, meta = {'items' : deepcopy(items)})

        except Exception as e:
            print(items['url'])
            print(items['title'])
            print('标题日期链接获取失败')
            print(e)
            pass

    def parse_article(self, response):
        try:
            items = response.meta['items']
            dirty_article = response.text
            # 使用正则获取文本内容
            # dirty_text = re.search(r'<head>(.*?)<\/html>', article_text, re.S).group(1)
            clean_article = re.sub(eval(self.regularExpression), ' ', dirty_article)

            # 地方名称编号
            items["addr_id"] = '431'
            # 系统时间，时间戳
            items["time"] = '%.0f' % time.time()
            # 文章来源
            items["source_name"] = '湖南省政府采购网'
            # 分类id
            items["sheet_id"] = '29'
            # 文本内容
            items['intro'] = clean_article
            yield items

        except Exception as e:
            print(items['url'])
            print(items['title'])
            print('获取文章出错')
            print(e)
            pass
