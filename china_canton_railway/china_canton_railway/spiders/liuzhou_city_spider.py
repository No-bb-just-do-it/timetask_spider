# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category
import re
from utils.STMP import send_mail_when_error
from utils.parse_content import pc
from urllib import parse

# http://www.gxlzzb.com/gxlzzbw/jyxx/001004/ @ 柳州市公共资源交易管理办公室
class liuzhouSpiderSpider(scrapy.Spider):
    name = 'liuzhou_city_gov_spider'

    def __init__(self):

        self.city_dict = get_city_dict()
        self.category = category

        self.baseUrl = 'http://www.gxlzzb.com'

        self.xpath_rule = {
            'title_rule': './td/div/a/@title',
            'url_rule': './td/div/a/@href',
            'web_time_rule': './/span[@class="wb-data-date"]/text()',
            'content_rule' : r'<div class="news-article">(.*?)<!-- footer -->'
        }

        self.error_count = 0
        self.source_name = '柳州市公共资源交易服务中心网站'

        self.regularExpression = regularExpression
        self.regularExpression02 = regularExpression02

        self.addr_id = '416'

        self.headers = {
            'Host': 'www.gxlzzb.com',
            'Referer': 'http://www.gxlzzb.com/gxlzzbw/showinfo/jyxxmore.aspx?catgorynum1=004&catgorynum2=006&xiaqu=&type=2'
        }

        self.pc = pc

        self.gov_bidNotice_url = 'http://www.gxlzzb.com/gxlzzbw/showinfo/jyxxmore.aspx?catgorynum1=004&catgorynum2=006&xiaqu=&type=2'

        self.VIEWSTATE = ''
        self.VIEWSTATEGENERATOR = 'D38D4441'
        self.EVENTTARGET = 'JyxxSearch1%24Pager'
        self.count = 1

    def start_requests(self):
        yield scrapy.Request(url = self.gov_bidNotice_url, callback = self.parse, headers = self.headers)

    def parse(self, response):
        VIEWSTATE = re.search(r'value="(.*?)"', response.text, re.S).group(1)
        print(VIEWSTATE)

        infos = response.xpath('//table[@class="wb-data-item"]//tr')

        for each_li in infos:
            items = {}
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

            print(items)

        if self.count < 3:
            self.count += 1
            data = {
                '__VIEWSTATE' : VIEWSTATE.strip(),
                '__VIEWSTATEGENERATOR' : self.VIEWSTATEGENERATOR,
                '__EVENTTARGET' : self.EVENTTARGET,
                '__EVENTARGUMENT' : str(self.count),
                'JyxxSearch1$Pager_input' : '1'

            }
            yield scrapy.FormRequest(url = 'http://www.gxlzzb.com/gxlzzbw/showinfo/jyxxmore.aspx?catgorynum1=004&catgorynum2=006&xiaqu=&type=2', callback = self.parse, dont_filter = True, formdata = data, headers = self.headers)
