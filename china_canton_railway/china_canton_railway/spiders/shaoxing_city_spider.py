# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category
import re
from utils.STMP import send_mail_when_error
from utils.parse_content import pc

# http://ggb.sx.gov.cn/ @ 绍兴公共资源交易网
class shaoxingSpiderSpider(scrapy.Spider):
    name = 'shaoxing_city_gov_spider'

    def __init__(self):

        self.city_dict = get_city_dict()
        self.category = category

        self.baseUrl = 'http://ggb.sx.gov.cn'

        self.xpath_rule = {
            'content_rule' : r'<meta name="ContentStart">(.*?)<meta name="ContentEnd">'
        }

        self.error_count = 0
        self.source_name = '绍兴公共资源交易网'

        self.regularExpression = regularExpression
        self.regularExpression02 = regularExpression02

        self.addr_id = '401'

        self.headers = {
            'Host': 'ggb.sx.gov.cn',
            'Referer': 'http://ggb.sx.gov.cn/'
        }

        self.pc = pc

        self.start_urls = [
            # 市级政府采购 招标公告 共174页 中标公告 共146页 废标公告 共35页 每天更新跨度各一页
            ('招标公告', 'http://ggb.sx.gov.cn/module/jpage/dataproxy.jsp?col=1&appid=1&webid=3003&path=%2F&columnid=1518860&sourceContentType=1&unitid=4685909&webname=%E7%BB%8D%E5%85%B4%E5%85%AC%E5%85%B1%E8%B5%84%E6%BA%90%E4%BA%A4%E6%98%93%E7%BD%91&permissiontype=0&startrecord={}&endrecord={}&perpage=15', 3),
            ('招标结果', 'http://ggb.sx.gov.cn/module/jpage/dataproxy.jsp?col=1&appid=1&webid=3003&path=%2F&columnid=1518861&sourceContentType=1&unitid=4685909&webname=%E7%BB%8D%E5%85%B4%E5%85%AC%E5%85%B1%E8%B5%84%E6%BA%90%E4%BA%A4%E6%98%93%E7%BD%91&permissiontype=0&startrecord={}&endrecord={}&perpage=15', 3),
            ('招标结果', 'http://ggb.sx.gov.cn/module/jpage/dataproxy.jsp?col=1&appid=1&webid=3003&path=%2F&columnid=1518862&sourceContentType=1&unitid=4685909&webname=%E7%BB%8D%E5%85%B4%E5%85%AC%E5%85%B1%E8%B5%84%E6%BA%90%E4%BA%A4%E6%98%93%E7%BD%91&permissiontype=0&startrecord={}&endrecord={}&perpage=15', 3),
            # 县级政府采购 采购公告 共151页 中标公告 共100页 每天更新跨度各一页
            ('招标公告', 'http://ggb.sx.gov.cn/module/jpage/dataproxy.jsp?col=1&appid=1&webid=3003&path=%2F&columnid=1518895&sourceContentType=1&unitid=4685909&webname=%E7%BB%8D%E5%85%B4%E5%85%AC%E5%85%B1%E8%B5%84%E6%BA%90%E4%BA%A4%E6%98%93%E7%BD%91&permissiontype=0&startrecord={}&endrecord={}&perpage=15', 3),
            ('招标结果', 'http://ggb.sx.gov.cn/module/jpage/dataproxy.jsp?col=1&appid=1&webid=3003&path=%2F&columnid=1518896&sourceContentType=1&unitid=4685909&webname=%E7%BB%8D%E5%85%B4%E5%85%AC%E5%85%B1%E8%B5%84%E6%BA%90%E4%BA%A4%E6%98%93%E7%BD%91&permissiontype=0&startrecord={}&endrecord=90&perpage={}', 3),
            # 县级建设工程 招标公告 共75页 中标公示 共70页 成交结果 共43页 每天更新数据均一页
            ('招标公告', 'http://ggb.sx.gov.cn/module/jpage/dataproxy.jsp?col=1&appid=1&webid=3003&path=%2F&columnid=1518891&sourceContentType=1&unitid=4685909&webname=%E7%BB%8D%E5%85%B4%E5%85%AC%E5%85%B1%E8%B5%84%E6%BA%90%E4%BA%A4%E6%98%93%E7%BD%91&permissiontype=0&startrecord={}&endrecord={}&perpage=15', 3),
            ('招标结果', 'http://ggb.sx.gov.cn/module/jpage/dataproxy.jsp?col=1&appid=1&webid=3003&path=%2F&columnid=1518892&sourceContentType=1&unitid=4685909&webname=%E7%BB%8D%E5%85%B4%E5%85%AC%E5%85%B1%E8%B5%84%E6%BA%90%E4%BA%A4%E6%98%93%E7%BD%91&permissiontype=0&startrecord={}&endrecord={}&perpage=15', 3),
            ('招标结果', 'http://ggb.sx.gov.cn/module/jpage/dataproxy.jsp?col=1&appid=1&webid=3003&path=%2F&columnid=1518893&sourceContentType=1&unitid=4685909&webname=%E7%BB%8D%E5%85%B4%E5%85%AC%E5%85%B1%E8%B5%84%E6%BA%90%E4%BA%A4%E6%98%93%E7%BD%91&permissiontype=0&startrecord={}&endrecord={}&perpage=15', 3),
        ]


    def start_requests(self):
        for url_info in self.start_urls:
            urls = [url_info[1].format((x -1) * 45, x * 45) for x in range(1, url_info[2])]
            for url in urls:
                items = {}
                items['type_id'] = self.category[url_info[0]]
                yield scrapy.Request(url, callback=self.parse, meta={"items": deepcopy(items)}, headers = self.headers)


    def parse(self, response):
        items = response.meta['items']
        infos = re.findall('<a href=(.*?)</ul>', response.text, re.S)

        for each_li in infos:
            items['title'] = ''
            items['url'] = ''
            items['web_time'] = ''
            items['intro'] = ''
            items['addr_id'] = ''

            try:
                items['title'] = re.search(r'>(.*?)</a>', each_li, re.S).group(1)
            except:
                pass

            try:
                items['url'] = self.baseUrl + re.search(r'"(.*?)"', each_li, re.S).group(1)
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
                items['web_time'] = re.search(r'\[(.*?)\]', each_li, re.S).group(1)
            except:
                pass
            # print(items)
            yield scrapy.Request(items['url'], callback = self.parse_article, headers = self.headers, meta = {'items' : deepcopy(items)})


    def parse_article(self, response):
        items = response.meta['items']
        try:
            items['intro'] = self.pc.get_clean_content(self.xpath_rule['content_rule'], self.regularExpression, self.regularExpression02, response.text)
        except:
            pass

        items['addr_id'] = self.addr_id
        if items['addr_id'] == '':
            for city in self.city_dict:
                if city in items['title']:
                    items['addr_id'] = self.city_dict[city]
                    break

        items["source_name"] = self.source_name
        yield items