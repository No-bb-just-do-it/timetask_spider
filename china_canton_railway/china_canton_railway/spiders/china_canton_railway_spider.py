# -*- coding: utf-8 -*-
# 中国铁路广州局集团有限公司物资采购商务平台
import scrapy
from copy import deepcopy
import time
import re
from utils.STMP import send_mail_when_error
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, category
from utils.quit_spider import quit

class ChinaCantonRailwaySpiderSpider(scrapy.Spider):
    name = 'china_canton_railway_spider'
    allowed_domains = []
    # start_urls = ['http://95306.cn/']

    def __init__(self):

        self.city_dict = get_city_dict()
        self.regularExpression = regularExpression
        self.category = category

        # 文章拼接链接
        self.article_url = 'http://61.235.77.80/'

        self.pattern01 = r'成交人：(.*?)<'
        self.pattern_list = [self.pattern01]

        self.headers = {
            'Host': '61.235.77.80',
            'Referer': 'http://61.235.77.80/mainPageNoticeList.do?method=list&cur=1',
        }

        self.start_urls = [
            # 采购公告 共1601页 每天更新跨度10页
            ('招标公告', "http://wz.guangzh.95306.cn/mainPageNoticeList.do?method=init&id=1000001&cur={}&keyword=&inforCode=&time0=&time1=", 1601),
            # 中标结果 共598页 每天更新跨度6页
            ('招标结果', "http://wz.guangzh.95306.cn/mainPageNoticeList.do?method=init&id=1200001&cur={}&keyword=&inforCode=&time0=&time1=", 598),
            # 变更公告 共85页 每天更新跨度1页
            ('变更公告', "http://wz.guangzh.95306.cn/mainPageNoticeList.do?method=init&id=1300001&cur={}&keyword=&inforCode=&time0=&time1=", 85),
            # 采购公示 共487页 每天更新跨度3页
            ('招标结果', "http://wz.guangzh.95306.cn/mainPageNoticeList.do?method=init&id=1600001&cur={}&keyword=&inforCode=&time0=&time1=", 487),
            # 采购公示 共484页 每天更新跨度3页
            ('招标公告', "http://wz.guangzh.95306.cn/mainPageNoticeList.do?method=init&id=7000001&cur={}&keyword=&inforCode=&time0=&time1=", 484),
            # 结果公示 共39页 每天更新跨度3页
            ('招标结果', "http://wz.guangzh.95306.cn/mainPageNoticeList.do?method=init&id=7200001&cur={}&keyword=&inforCode=&time0=&time1=", 39)
        ]

    def start_requests(self):
        for url_info in self.start_urls:
            # 构造分页列表
            urls = [url_info[1].format(i) for i in range(1, url_info[2])]
            for url in urls:
                items = {}
                items["type_id"] = self.category[url_info[0]]
                yield scrapy.Request(url, callback=self.parse, meta={"items": deepcopy(items)}, headers = self.headers)

    def parse(self, response):
        items = response.meta['items']

        # 获取所有信息的所在tr标签
        all_trs = response.xpath('//table[@class="listInfoTable"]//tr')[1:]

        for each_tr in all_trs:

            items['title'] = ''
            items['url'] = ''
            items['web_time'] = ''
            items['intro'] = ''
            items['addr_id'] = ''

            try:
                items['title'] = each_tr.xpath('./td/@title').extract_first().replace('\r', '')
            except:
                pass

            try:
                items['url'] = self.article_url + each_tr.xpath('./td/a/@href').extract_first()
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
                items['web_time'] = each_tr.xpath('./td/following-sibling::td[4]/@title').extract_first().strip()
            except:
                pass

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
                    break

            yield scrapy.Request(url = items['url'], callback = self.parse_article, meta = {'items' : deepcopy(items)}, headers = self.headers)


    def parse_article(self, response):
        items = response.meta['items']
        dirty_text = response.text

        try:
            dirty_article = re.search(r'<div class="topTlt">(.*?)<input type="hidden" name="flagForward"', dirty_text,re.S).group(1)

            clean_article = re.sub(self.regularExpression, ' ', dirty_article)
            items['intro'] = clean_article
        except Exception as e:
            print('文章获取失败')
            print(e)
            pass

        try:
            items['title'] = items['title'].split('：', 1)[1]
        except:
            pass

        items["time"] = '%.0f' % time.time()
        items["source_name"] = '中国铁路广州局集团有限公司物资采购商务平台'
        yield items

