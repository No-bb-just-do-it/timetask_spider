# -*- coding: utf-8 -*-
from copy import deepcopy
from utils.STMP import send_mail_when_error
from .common_spider import CommonSpider
from utils.Regular_Expression import category
import scrapy

# http://www.jzggzy.com/TPFront_JingZhou/jyxx_jz/006002/006002001/ @ 荆州市公共资源交易信息网
class puerSpiderSpider(CommonSpider):
    name = 'puer_city_gov_spider'

    def __init__(self):
        self.baseUrl = 'http://www.pesggzyjyxxw.com'

        self.xpath_rule = {
            'list_page' : '//div[@class="news"]//tr',
            'title_rule': './td[3]/a/@title',
            'url_rule': './td[3]/a/@href',
            'web_time_rule': './td[4]/text()',
            'content_rule' : r'<div class="news-title">(.*?)<div class="foot row">'
        }

        self.error_count = 0
        self.source_name = '普洱市公共资源交易电子服务系统'
        self.category = category
        self.addr_id = '427'

        self.headers = {
            'Host': 'www.pesggzyjyxxw.com',
            'Referer': 'http://www.pesggzyjyxxw.com/jyxx/jsgcZbgg?currentPage=1&scrollValue=0'
        }

        self.start_urls = [
            # 工程招标 招标公告56 变更公告55 中标公告57 每天更新跨度均一
            ('招标公告', 'http://www.pesggzyjyxxw.com/jyxx/jsgcZbgg?currentPage={}&scrollValue=0', 3),
            ('变更公告', 'http://www.pesggzyjyxxw.com/jyxx/jsgcBgtz?currentPage={}&scrollValue=0', 3),
            ('招标结果', 'http://www.pesggzyjyxxw.com/jyxx/jsgcZbjggs?currentPage={}&scrollValue=0', 3),
            # 政府采购 招标公告共79页 变更公告33 结果公告58页
            ('招标公告', 'http://www.pesggzyjyxxw.com/jyxx/zfcg/cggg?currentPage={}&scrollValue=0&area=008', 3),
            ('变更公告', 'http://www.pesggzyjyxxw.com/jyxx/zfcg/gzsx?currentPage={}&scrollValue=0', 3),
            ('招标结果', 'http://www.pesggzyjyxxw.com/jyxx/zfcg/zbjggs?currentPage={}&scrollValue=0', 3),
        ]


    def parse(self, response):
        items = response.meta['items']

        infos = response.xpath(self.xpath_rule['list_page'])

        for each_li in infos[1:]:
            items['title'] = ''
            items['url'] = ''
            items['web_time'] = ''
            items['intro'] = ''
            items['addr_id'] = ''

            # 在这里之所以分这么细、是因为建设工程的tr标签每个都不一样、但是政府采购则全部一样
            try:
                if 'jsgcZbgg' in response.url or 'zfcg' in response.url:
                    items['title'] = ''.join(each_li.xpath(self.xpath_rule['title_rule']).extract()).strip()
                elif 'jsgcBgtz' in response.url:
                    items['title'] = ''.join(each_li.xpath('./td[4]/a/@title').extract()).strip()
                else:
                    items['title'] = ''.join(each_li.xpath('./td[3]/@title').extract()).strip()
            except:
                pass

            try:
                if 'jsgcZbgg' in response.url or 'jsgcZbjggs' in response.url or 'zfcg' in response.url:
                    items['url'] = self.baseUrl + each_li.xpath(self.xpath_rule['url_rule']).extract_first()
                else:
                    items['url'] = self.baseUrl + ''.join(each_li.xpath('./td[4]/a/@href').extract()).strip()
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
                if 'jsgcZbgg' in response.url or 'jsgcZbjggs' in response.url or 'zfcg' in response.url:
                    items['web_time'] = each_li.xpath(self.xpath_rule['web_time_rule']).extract_first().strip()
                else:
                    items['web_time'] = ''.join(each_li.xpath('./td[5]/text()').extract()).strip()
            except:
                pass
            yield scrapy.Request(items['url'], callback = self.parse_article, headers = self.headers, meta = {'items' : deepcopy(items)})