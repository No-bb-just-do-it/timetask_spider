# -*- coding: utf-8 -*-
import re
from copy import deepcopy

import PyV8
import scrapy
from utils.STMP import send_mail_when_error
from .common_spider import CommonSpider
from utils.Regular_Expression import category, regularExpression02, regularExpression
from utils.encode_url import aes

# http://ggzy.xzsp.tj.gov.cn/jyxxzfcg/index.jhtml @ 天津市公共资源交易网
class tianjinSpiderSpider(CommonSpider):
    name = 'tianjin_city_gov_spider'

    def __init__(self):

        self.baseUrl = ''
        self.error_count = 0
        self.source_name = '天津市公共资源交易网'
        self.addr_id = '408'
        self.category = category

        self.xpath_rule = {
            'list_page' : '//div[@class="article-content"]/ul/li',
            'title_rule' : './div/a//text()',
            'url_rule' : './div/a/@href',
            'web_time_rule' : './div/div/text()',
            # 'content_rule' : r'<div class="content" id="zoom">(.*?)<!-- bottom begin-->'
        }

        self.headers = {
            'Host': 'ggzy.xzsp.tj.gov.cn',
            'Connection': 'keep-alive',
            'Referer': 'http://ggzy.xzsp.tj.gov.cn/jyxxgcjs/index.jhtml'
        }

        self.execute = PyV8.JSContext()
        self.execute.enter()
        with open('utils/ase_encryption.js')as f:
            self.a = f.read()

        self.start_urls = [
            # 政府采购 1767页 每天更新跨度2页 公告 更正 结果都在一起
            ('招标公告', 'http://ggzy.xzsp.tj.gov.cn/jyxxzfcg/index_{}.jhtml', 3),
            # 工程建设 9016 每天更新跨度5页 公告 更正 结果都在一起
            ('招标公告', 'http://ggzy.xzsp.tj.gov.cn/jyxxgcjs/index_{}.jhtml', 3),
            # 医疗采购 38 每天更新1页 公告 更正 结果都在一起
            ('招标公告', 'http://ggzy.xzsp.tj.gov.cn/jyxxyy/index_{}.jhtml', 3),
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
                items['title'] = ''.join(each_li.xpath(self.xpath_rule['title_rule']).extract()).strip()
            except:
                pass

            try:
                get_url = self.baseUrl + each_li.xpath(self.xpath_rule['url_rule']).extract_first()
                get_prefix = re.search(r'(http://ggzy.xzsp.tj.gov.cn:80/jyxx.*?/)', get_url, re.S).group(1)
                dirty_url = aes.url_encrypt(get_url)
                suffix_url = re.search(r'http://ggzy.xzsp.tj.gov.cn:80/jyxx.*?/(.*)', dirty_url, re.S).group(1)
                if '/' in suffix_url:
                    items['url'] = get_prefix + suffix_url.replace('/', '%5E')
                else:
                    items['url'] = dirty_url

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
                items['web_time'] = each_li.xpath(self.xpath_rule['web_time_rule']).extract_first().strip()
            except:
                pass
            yield scrapy.Request(items['url'], callback = self.parse_article, headers = self.headers, meta = {'items' : deepcopy(items)})

    def parse_article(self, response):
        items = response.meta['items']

        content = re.search(r'content="(.*?)"', response.text, re.S).group(1)
        hehe = '''
        (function(){
            		var a=''' + '"{}"'.format(content) + ''';
            		if(typeof(a)=='undefined'){
            			return ;
            		}
            		var b=a.length;
            		var d=a.substring(b-16,b);
        			var k = CryptoJS.enc.Utf8.parse(d);
        			var en = CryptoJS.AES.decrypt(a, k, {mode:CryptoJS.mode.ECB,padding: CryptoJS.pad.Pkcs7});
        			var c=CryptoJS.enc.Utf8.stringify(en).toString();
        			return c;
            	});
        '''

        result = self.execute.eval(self.a + hehe)
        dirty_article = result()

        try:
            dirty_article = re.sub(regularExpression02, '>', dirty_article)
            clean_article = re.sub(regularExpression, ' ', dirty_article)
            items['intro'] = clean_article
        except:
            pass

        items['addr_id'] = self.addr_id
        if items['addr_id'] == '':
            for city in self.city_dict:
                if city in items['title']:
                    items['addr_id'] = self.city_dict[city]
                    break

        if '中标' in items['title'] or '成交' in items['title'] or '结果' in items['title']:
            items['type_id'] = '38257'
        elif '更正' in items['title'] or '变更' in items['title']:
            items['type_id'] = '38256'

        if items['addr_id'] == '':
            for city in self.city_dict:
                if city in items['title']:
                    items['addr_id'] = self.city_dict[city]
                    break

        items["source_name"] = self.source_name
        yield items