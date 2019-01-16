# -*- coding: utf-8 -*-
from copy import deepcopy
from scrapy.exceptions import CloseSpider
from STMP import send_mail_when_error
import scrapy
import re
import time
# import logging


class ChinaUnicomConprehensiveSpider(scrapy.Spider):
    name = 'china_unicom_comprehensive'
    allowed_domains = ['chinaunicombidding.cn']
    # start_urls = ['http://chinaunicombidding.cn/']

    def __init__(self):
        self.city_dict = {}
        # 将各个城市与编号制成字典
        with open('城市编号id.txt', 'r', encoding = 'GB2312')as f:
            city_data = f.read()
            for each_info in city_data.split('\n'):
                self.city_dict[each_info.split(',')[0]] = each_info.split(',')[1]

        with open('/root/RegularExpression.txt', 'r')as f:
            self.regularExpression = f.read()

        # 采购公告
        self.bid_Notice_url = 'http://www.chinaunicombidding.cn/jsp/cnceb/web/info1/infoList.jsp?page={}&type=1'
        # 采购结果
        self.bid_dealNotice_url = 'http://www.chinaunicombidding.cn/jsp/cnceb/web/info1/infoList.jsp?page={}&type=2'
        # 单一来源采购
        self.single_source_url = 'http://www.chinaunicombidding.cn/jsp/cnceb/web/info1/infoList.jsp?page={}&type=3'
        # 文章拼接链接
        self.base_url = 'http://www.chinaunicombidding.cn'


    def start_requests(self):
        # 招标公告 总共5900页 每天跨度22~30页
        for page in range(1, 21):
            items = {}
            items['type_id'] = '38255'
            yield scrapy.Request(
                url=self.bid_Notice_url.format(page), callback=self.parse,
                meta={'items': deepcopy(items)}, dont_filter=True
            )

        # 单一来源 总共18页 每天跨度5~7页
        for page in range(1, 5):
            items = {}
            items['type_id'] = '38255'
            yield scrapy.Request(
                url=self.single_source_url.format(page), callback=self.parse,
                meta={'items': deepcopy(items)}, dont_filter=True
            )

        # 招标结果 总共50页 每天跨度20页
        for page in range(1, 15):
            items = {}
            items['type_id'] = '38257'
            yield scrapy.Request(
                url=self.bid_dealNotice_url.format(page), callback=self.parse,
                meta={'items': deepcopy(items)}, dont_filter=True
            )

    def parse(self, response):
        try:
            items = response.meta['items']
            # 获取列表页文章的tr标签
            all_trs = response.xpath('//div[@id="div1"]//tr')

            for each_tr in all_trs:
                items['title'] = each_tr.xpath('.//span/@title').extract_first().strip()

                # 如果标题出现失败、基本可以证明是失败公示、所以将其纳入38257
                if '失败' in items['title']:
                    items['type_id'] = '38257'

                # 获取文章id、然后使用网页前缀拼接文章id获取到文章的真实id
                article_url = each_tr.xpath('.//span/@onclick').extract_first()
                items['url'] = self.base_url + re.search(r'window.open\("(.*?)","",', article_url, re.S).group(1)

                # 获取日期
                items['web_time'] = each_tr.xpath('.//td/following-sibling::td/text()').extract()[0].strip()

                # 获取到地址然后通过城市表获取城市id
                try:
                    address = each_tr.xpath('.//td/following-sibling::td/text()').extract()[1].strip()
                    for each_city in self.city_dict:
                        if each_city in address:
                            items['addr_id'] = self.city_dict[each_city]
                            break
                except:
                    pass

                # 如果从地址栏找不到地址 则从标题获取
                if 'addr_id' not in items:
                    for each_city in self.city_dict:
                        if each_city in items['title']:
                            items['addr_id'] = self.city_dict[each_city]
                            break

                # 如果地址栏和标题都无法获取到地址、则使用默认地址全国
                if 'addr_id' not in items:
                    items['addr_id'] = '100'


                yield scrapy.Request(url = items['url'], callback=self.article_parse, meta={'items':deepcopy(items)})

        except Exception as e:
            print(items['url'])
            print(items['title'])
            print(e)
            print('标题链接日期获取出错')

    def article_parse(self, response):
        try:
            items = response.meta['items']

            # 通过正则获取正文内容
            dirty_article = response.text
            dirty_article = re.search(r'<P style="TEXT-ALIGN: center" class=MsoNormal align=center>(.*?)</BODY></html>',dirty_article, re.S).group(1)
            # 将文章的垃圾数据进行清洗
            clean_article = re.sub(eval(self.regularExpression), ' ', dirty_article)
            # 旧版
            # clean_article = re.sub(r'\r|\t|\n|<!--.*?-->|<input.*?>|class=[\'\"].*?[\'\"]|id=[\'\"].*?[\'\"]|style=[\'\"].*?[\'\"]|<STYLE.*?>.*?<\/STYLE>|class=\w*', ' ', dirty_article)

            # 系统时间，时间戳
            items["time"] = '%.0f' % time.time()
            # 分类id
            items["sheet_id"] = '29'
            # 文章来源
            items["source_name"] = '中国联通采购与招标网'
            # 内容
            items["intro"] = clean_article

            yield(items)
            # print(items)

        except Exception as e:
            print(items['url'])
            print(items['title'])
            print(e)
            print('文章提取出错')

