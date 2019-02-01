# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category
import re
from utils.STMP import send_mail_when_error
from utils.parse_content import pc
from urllib import parse

# http://www.gxlzzb.com/gxlzzbw//showinfo/jyxxmore.aspx?catgorynum1=&catgorynum2=&xiaqu=&type=1 @ 柳州市公共资源交易管理办公室
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
            'content_rule' : r'<td id="TDContent".*?>(.*?)<td id="authorTd'
        }

        self.error_count = 0
        self.source_name = '柳州市公共资源交易服务中心网站'

        self.regularExpression = regularExpression
        self.regularExpression02 = regularExpression02

        self.addr_id = '416'

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Host': 'www.gxlzzb.com',
            'Origin': 'http://www.gxlzzb.com'
        }

        self.pc = pc

        self.gov_bidNotice_url = 'http://www.gxlzzb.com/gxlzzbw//showinfo/jyxxmore.aspx?catgorynum1=&catgorynum2=&xiaqu=&type=1'

        self.VIEWSTATE = ''
        self.VIEWSTATEGENERATOR = 'D38D4441'
        self.EVENTTARGET = 'JyxxSearch1%24Pager'
        self.count = 1

    def start_requests(self):
        yield scrapy.Request(url = self.gov_bidNotice_url, callback = self.parse, headers = self.headers, dont_filter = True)

    def parse(self, response):
        VIEWSTATE = re.search(r'value="(.*?)"', response.text, re.S).group(1)
        # print(VIEWSTATE)

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
            print(items['title'])

            # yield scrapy.Request(url = items['url'], callback = self.parse_article, headers = self.headers, meta = {'items' : deepcopy(items)})

        # 总共1443页
        if self.count < 3:
            self.count += 1

            form_data = {
                '__VIEWSTATE' : VIEWSTATE,
                '__VIEWSTATEGENERATOR' : 'D38D4441',
                '__EVENTTARGET' : 'JyxxSearch1$Pager',
                '__EVENTARGUMENT' : str(self.count),
                'JyxxSearch1$Pager_input' : '1',
                '__VIEWSTATEENCRYPTED' : ''
            }
            yield scrapy.FormRequest(url = self.gov_bidNotice_url, callback = self.parse, dont_filter = True, formdata = form_data, headers = self.headers)
    #
    #
    # def parse_article(self, response):
    #     items = response.meta['items']
    #
    #     try:
    #         items['intro'] = self.pc.get_clean_content(self.xpath_rule['content_rule'], self.regularExpression, self.regularExpression02, response.text)
    #     except:
    #         pass
    #
    #
    #     items['addr_id'] = self.addr_id
    #
    #     if items['addr_id'] == '':
    #         for city in self.city_dict:
    #             if city in items['title']:
    #                 items['addr_id'] = self.city_dict[city]
    #                 break
    #
    #     if '中标' in items['title'] or '废标' in items['title']:
    #         items['type_id'] = '38257'
    #     elif '变更' in items['title'] or '更正' in items['title']:
    #         items['type_id'] = '38256'
    #     else:
    #         items['type_id'] = '38255'
    #
    #     items["source_name"] = self.source_name
    #     yield items
