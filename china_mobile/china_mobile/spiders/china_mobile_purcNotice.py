# -*- coding: utf-8 -*-
import logging
import random
import re
import time
from copy import deepcopy
from datetime import datetime, date, timedelta
# 1. 修改继承关系: 继承RedisCrawlSpider
from scrapy_redis.spiders import RedisCrawlSpider
import redis
import scrapy
from scrapy.exceptions import CloseSpider
from STMP import send_mail_when_error
# https://b2b.10086.cn/b2b/main/preIndex.html

class ChinaMobilePurcnoticeSpider(scrapy.Spider):
    name = 'china_mobile_purcNotice'
    allowed_domains = ['10086.cn']
    # start_urls = ['http://10086.cn/']

    def __init__(self):
        self.spider_name = 'china_mobile_purcNotice'
        # 采购公告url  (用于post请求)  页码总数11118页 每天数据量跨度11~15页左右
        self.china_mobile_purchase_Notice = 'https://b2b.10086.cn/b2b/main/listVendorNoticeResult.html?noticeBean.noticeType=2'
        # 预审公告   页码总数41页    每天数据跨度1页
        self.china_mobile_pre_Notice = 'https://b2b.10086.cn/b2b/main/listVendorNoticeResult.html?noticeBean.noticeType=3'
        # 候选人公示 总页数5232    每天数据跨度7~10页
        self.china_mobile_condidate_Notice = 'https://b2b.10086.cn/b2b/main/listVendorNoticeResult.html?noticeBean.noticeType=7'
        # 中标结果 总页数524    每天数据跨度9~12页
        self.china_mobile_deal_Notice = 'https://b2b.10086.cn/b2b/main/listVendorNoticeResult.html?noticeBean.noticeType=16'
        # 单一来源采购信息公告 总页数3118    每天数据跨度9~12页
        self.china_mobile_single_source_Notice = 'https://b2b.10086.cn/b2b/main/listVendorNoticeResult.html?noticeBean.noticeType=1'

        # 原文章url
        self.article_url = 'https://b2b.10086.cn/b2b/main/viewNoticeContent.html?noticeBean.id={}'

        self.pattern01 = r'服务地点(.*?)</span>'
        self.pattern02 = r'公司地\s*址：(.*?)</span>'
        self.pattern03 = r'地.*?址：(.*?)</span>'
        self.pattern04 = r'详细地址：(.*?)</span>'
        self.pattern05 = r'招标方：(.*?)</span>'
        self.pattern06 = r'采购人：(.*?)</span>'
        self.pattern08 = r'联系地址：</span><span style="font-family:宋体;color:black;">(.*?)</span>'
        # 正则表达式的规则列表
        self.pattern_list = [self.pattern08, self.pattern01, self.pattern02, self.pattern03, self.pattern04, self.pattern05, self.pattern06]

        with open('/root/RegularExpression.txt', 'r')as f:
            self.regularExpression = f.read()

        self.city_dict = {}
        # 将各个城市与编号制成字典
        with open('城市编号id.txt', 'r', encoding='GB2312')as f:
            city_data = f.read()
            for each_info in city_data.split('\n'):
                self.city_dict[each_info.split(',')[0]] = each_info.split(',')[1]


    def start_requests(self):
        # 采购公告url  (用于post请求)  页码总数11436页 每天数据量跨度11~15页左右 设置21页
        for page in range(1, 21):
            data = {
                'page.currentPage': str(page),
                'page.perPageSize': '20',
                'noticeBean.sourceCH': '',
                'noticeBean.source': '',
                'noticeBean.title': '',
                'noticeBean.startDate': '',
                'noticeBean.endDate': ''
            }
            items = {}
            items['type_id'] = '38255'
            yield scrapy.FormRequest(
                    url = self.china_mobile_purchase_Notice,
                    formdata = data,
                    callback = self.parse,
                    meta = {'items' : deepcopy(items)},
                    dont_filter=True
            )

        # 预审公告   页码总数42页    每天数据跨度1页
        for page in range(1, 3):
            data = {
                'page.currentPage': str(page),
                'page.perPageSize': '20',
                'noticeBean.sourceCH': '',
                'noticeBean.source': '',
                'noticeBean.title': '',
                'noticeBean.startDate': '',
                'noticeBean.endDate': ''
            }
            items = {}
            items['type_id'] = '38255'
            yield scrapy.FormRequest(
                url=self.china_mobile_pre_Notice,
                formdata=data,
                callback=self.parse,
                meta={'items': deepcopy(items)},
                dont_filter=True
            )

        # 候选人公示 总页数5356    每天数据跨度7~10页 设置11页
        for page in range(1, 11):
            data = {
                'page.currentPage': str(page),
                'page.perPageSize': '20',
                'noticeBean.sourceCH': '',
                'noticeBean.source': '',
                'noticeBean.title': '',
                'noticeBean.startDate': '',
                'noticeBean.endDate': ''
            }
            items = {}
            items['type_id'] = '38255'
            yield scrapy.FormRequest(
                url=self.china_mobile_condidate_Notice,
                formdata=data,
                callback=self.parse,
                meta={'items': deepcopy(items)},
                dont_filter=True
            )

        # 中标结果 总页数637    每天数据跨度9~12页 设置12页
        for page in range(1, 12):
            data = {
                'page.currentPage': str(page),
                'page.perPageSize': '20',
                'noticeBean.sourceCH': '',
                'noticeBean.source': '',
                'noticeBean.title': '',
                'noticeBean.startDate': '',
                'noticeBean.endDate': ''
            }
            items = {}
            items['type_id'] = '38257'
            yield scrapy.FormRequest(
                url=self.china_mobile_deal_Notice,
                formdata=data,
                callback=self.parse,
                meta={'items': deepcopy(items)},
                dont_filter=True
            )


        # 单一来源采购信息公告 总页数3308    每天数据跨度9~12页  设置12页
        for page in range(1, 12):
            data = {
                'page.currentPage': str(page),
                'page.perPageSize': '20',
                'noticeBean.sourceCH': '',
                'noticeBean.source': '',
                'noticeBean.title': '',
                'noticeBean.startDate': '',
                'noticeBean.endDate': ''
            }
            items = {}
            items['type_id'] = '38255'
            yield scrapy.FormRequest(
                url=self.china_mobile_single_source_Notice,
                formdata=data,
                callback=self.parse,
                meta={'items': deepcopy(items)},
                dont_filter = True
            )


    def parse(self, response):
        try:
            # 获取上个函数所传递的信息
            items = response.meta['items']
            # 获取所有tr标签中的前两个 因为前两个并非正常文章标签 所以可以忽略
            all_trs = response.xpath('//table[@class = "zb_result_table"]/tr')
            # 所获取到的all_trs标签为22个， 前两个是空字段、所以使用[2:]
            for each_article in all_trs[2:]:
                # 获取文章标题 由于有些tr标签没有title属性
                items['title'] = each_article.xpath('.//a/@title').extract_first()
                if items['title'] == None:
                    items['title'] = each_article.xpath('.//a/text()').extract_first()
                # 获取id 但并不是纯净的id 而是：selectResult('513159')
                dirty_article_id = each_article.xpath('./@onclick').extract_first()
                # 使用正则获取id
                article_id = re.search(r"\('(.*?)'\)", dirty_article_id).group(1)
                # 获取到id之后只用利用文章url跟文章id拼接
                items['url'] = self.article_url.format(article_id)
                # 获取日期 通过xpath的兄弟节点获取 当前节下的tr标签，然后通过following-sibling::td[3]获取到tr标签的第四个兄弟标签
                items['web_time'] = each_article.xpath('./td/following-sibling::td[3]/text()').extract_first()
                yield scrapy.Request(url = items['url'], callback = self.parse_article, meta = {'items' : deepcopy(items)})

        except Exception as e:
            print('标题链接日期获取失败')
            print(items['url'])
            print(items['title'])
            print(e)
            pass


    def parse_article(self, response):
        try:
            # 获取上个函数所传递的信息
            items = response.meta['items']
            # 解析
            article_text = response.text
            # 从正则中获取数据
            # 旧版
            # dirty_article = re.search(
            #     r'<img  src="\/b2b\/supplier\/b2bStyle\/img\/images\/con_pri_ws_002\.gif"  onclick="printView\(\)"\/>(.*?)<div class=" footer">',
            #     article_text, re.S).group(1)
            # 新版
            dirty_article = re.search(
                r'onclick="printView\(\)"/>(.*?)<div class=" footer"', article_text, re.S
            ).group(1)

            # 将文章的垃圾数据进行清洗（新版）
            clean_article = re.sub(eval(self.regularExpression), ' ', dirty_article)
            # 旧版
            # clean_article = re.sub(r'\r|\t|\n|<!--.*?-->|<input.*?>|class=[\'\"].*?[\'\"]|id=[\'\"].*?[\'\"]|style=[\'\"].*?[\'\"]|<STYLE.*?>.*?<\/STYLE>|class=\w*', ' ', dirty_article)

            # 遍历城市名 获取城市id 如果获取到就break
            for city_name in self.city_dict:
                if city_name in items['title']:
                    items['addr_id'] = self.city_dict[city_name]
                    break

            # 因为根据标题获取地名有时候会获取不到、所以再进行多一层判断从正文中获取地市名
            if 'addr_id' not in items:
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
                    break

            # 如果经过两层获取地址都无法获取到，  则使用默认地址
            if 'addr_id' not in items:
                items['addr_id'] = '100'

            # 系统时间，时间戳
            items["time"] = '%.0f' % time.time()
            # 分类id
            items["sheet_id"] = '29'
            # 文章来源
            items["source_name"] = '中国移动采购与招标网'
            # 内容
            items["intro"] = clean_article.strip()
            yield items

        except Exception as e:
            print('文章获取失败')
            print(items['url'])
            print(items['title'])
            print(e)
            pass
