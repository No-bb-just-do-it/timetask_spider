# -*- coding: utf-8 -*-
# 中国电信阳光采集网
import re
import time
from copy import deepcopy
import scrapy
from scrapy_redis.spiders import RedisSpider

class ChinaTelecomPurchaseInfosSpider(scrapy.Spider):
    name = 'china_telecom_purchase_infos'
    allowed_domains = []
    # start_urls = ['http://baidu.com/']
    # redis_key = 'china_telecom:start_urls'

    def __init__(self):
        self.headers = {
            'Referer': 'https://caigou.chinatelecom.com.cn/MSS-PORTAL/announcementjoin/list.do?provinceJT=NJT',
            'Host': 'caigou.chinatelecom.com.cn',
            'Origin': 'https://caigou.chinatelecom.com.cn',
            'Connection': 'keep-alive'
        }
        #  采购结果
        self.purchase_dealNotice = 'https://caigou.chinatelecom.com.cn/MSS-PORTAL/resultannounc/listForAd.do?provinceJT=NJT&paging.start={}&paging.pageSize=40&pageNum=10&goPageNum=1'
        # 采购澄清
        self.clearify_Notice = 'https://caigou.chinatelecom.com.cn/MSS-PORTAL/clearifynotice/listForAd.do?provinceJT=NJT&paging.start={}&paging.pageSize=40&pageNum=10&goPageNum=1'
        # 采购公告
        self.purchase_Notice = 'https://caigou.chinatelecom.com.cn/MSS-PORTAL/announcementjoin/list.do?provinceJT=NJT'
        # 资格预审公告列表
        self.qulify_Notice = 'https://caigou.chinatelecom.com.cn/MSS-PORTAL/prequalfication/listForAd.do?provinceJT=NJT&paging.start=1&paging.pageSize=40&pageNum=10&goPageNum=1'

        # 文章链接、需要使用format拼接  id在前、encryCode在后
        # 采购结果的文章地址链接
        self.dealNotice_url = 'caigou.chinatelecom.com.cn/MSS-PORTAL/resultannounc/viewHome.do?id={}&encryCode={}'
        # 预审公告的文章地址拼接
        self.pre_check_url = 'caigou.chinatelecom.com.cn/MSS-PORTAL/prequalfication/viewForAd.do?id={}&encryCode={}'
        # 澄清公告的文章地址拼接
        self.clearify_notice_url = 'caigou.chinatelecom.com.cn/MSS-PORTAL/clearifynotice/viewHome.do?id={}&encryCode={}'
        # 采购公告的文章地址拼接
        self.purchase_Notice_url = 'caigou.chinatelecom.com.cn/MSS-PORTAL/{}/viewHome.do?encryCode={}&id={}'
        # 单一来源采购公示
        self.single_source_url = 'caigou.chinatelecom.com.cn/MSS-PORTAL/purchaseannouncebasic/viewHome.do?encryCode={}&id={}'

        self.city_dict = {}
        # 将各个城市与编号制成字典
        with open('城市编号id.txt', 'r', encoding='GB2312')as f:
            city_data = f.read()
            for each_info in city_data.split('\n'):
                self.city_dict[each_info.split(',')[0]] = each_info.split(',')[1]

        with open('/root/RegularExpression.txt', 'r')as f:
            self.regularExpression = f.read()

    def start_requests(self):
        # 采购结果公示 总共页数2899 每天数据跨度15页左右
        for page in range(0, 15):
            items = {}
            items['category'] = '其他'
            items['type_id'] = '38257'
            yield scrapy.Request(url = self.purchase_dealNotice.format(int(page) * 40 + 1), callback = self.parse, meta = {'items' : deepcopy(items)}, dont_filter=True)

        # 采购公告澄清 总共页数7 每天数据跨度1页左右
        for page in range(0, 3):
            items = {}
            items['category'] = '采购公告澄清'
            items['type_id'] = '38255'
            yield scrapy.Request(url=self.clearify_Notice.format(int(page) * 40 + 1), callback=self.parse,
                                 meta={'items': deepcopy(items)}, dont_filter=True)

        # 采购公告 总共页数74 每天数据跨度30页左右
        for page in range(0, 30):
            data = {
                'provinceJT': 'NJT',
                'docTitle': '',
                'docCode': '',
                'provinceCode': '',
                'provinceNames': '',
                'startDate': '',
                'endDate': '',
                'docType': '',
                'paging.start': str(int(page) * 40 + 1),
                'paging.pageSize': '40',
                'pageNum': '40',
                'goPageNum': '1'
            }
            items = {}
            items['category'] = '采购公告'
            items['type_id'] = '38255'
            yield scrapy.FormRequest(
                url=self.purchase_Notice, formdata = data, callback=self.parse,
                                 meta={'items': deepcopy(items)}, headers = self.headers, dont_filter=True)

        # 资格预审公告 总共页数1 每天数据跨度1页左右
        for page in range(0, 2):
            items = {}
            items['category'] = '预审公告'
            items['type_id'] = '38255'
            yield scrapy.Request(url=self.qulify_Notice, callback=self.parse,
                                 meta={'items': deepcopy(items)}, dont_filter=True)

    def parse(self, response):
        # 因为做分布式的时候无法在构建url的时候添加category字段  所以通过这种方法来添加 用于每个category对应不同的提取方法
        # if 'resultannounc' or 'clearifynotice' in response.url:
        #     items = {}
        #     items['category'] = '其他'
        # elif 'announcementjoin' in response.url:
        #     items = {}
        #     items['category'] = '采购公告'
        # elif 'prequalfication' in response.url:
        #     items = {}
        #     items['category'] = '预审公告'

        try:
            items = response.meta['items']

            # 获取列表页的所有包含文章信息的tr标签
            all_trs = response.xpath('//table[@class="table_data"]/tr')
            # 第一个为列表的标题、所以无需提取
            for each_tr in all_trs[1:]:
                # 获取地址
                items['addr'] = each_tr.xpath('./td[1]/text()').extract_first()

                # 因为采购公告的html标签跟其他的公告不一样、所以使用if判断进行过滤(准确说应该是每个公告的html结构都不一样)
                # 获取拼接文章的所需的id、encryCode
                # view('1964','b463aa754dbe9d39604229a706eb9678');     dirty_article_id的格式
                if items['category'] == '采购公告':
                    items['viewCompare'] = each_tr.xpath('./td[5]/text()').extract_first().strip()
                    dirty_article_id = each_tr.xpath('./td[3]/a/@onclick').extract_first()
                elif items['category'] == '其他' or items['category'] == '采购公告澄清':
                    dirty_article_id = each_tr.xpath('./td[2]/a/@onclick').extract_first()
                # 预审公告
                else:
                    dirty_article_id = each_tr.xpath('./td[4]/a/@onclick').extract_first()


                # 获取采购公告文章id的正则表达式与另外三个有点不一样
                # view('1964','b463aa754dbe9d39604229a706eb9678');
                if items['category'] == '其他' or items['category'] == '预审公告' or items['category'] == '采购公告澄清':
                    # 使用正则获取文章id信息 该正则是使用在结果以及澄清公告
                    dirty_article_id = re.search(r"view\('(.*?)','(.*?)'\)", dirty_article_id)
                    # 分别将数据分配到各个变量
                    article_id, encryCode = dirty_article_id.group(1), dirty_article_id.group(2)
                else:
                    # onclick="view('5343314','cstldbkutGI=4dPqBw7iyVv3DLQAjIK+PMpr8Qzu0k7Y','58a900e7666ebaf5d1ae48995bd64b2f')"
                    # 使用正则获取信息 该正则式使用在采购公告
                    dirty_article_id = re.search(r"view\('(.*?)','(.*?)','(.*?)'\)", dirty_article_id)
                    # 分别将数据分配到各个变量
                    article_id, encryCode, url_category = dirty_article_id.group(1), dirty_article_id.group(3), dirty_article_id.group(2).lower()


                # 拼接每个分类的详情页url
                if items['category'] == '其他':
                    items['url'] = self.dealNotice_url.format(article_id, encryCode)

                elif  items['category'] == '采购公告':
                    if url_category == 'enquiry':
                        items['url'] = 'caigou.chinatelecom.com.cn/MSS-PORTAL/{}/viewForAd.do?encryCode={}&id={}'.format(url_category, encryCode, article_id)
                    elif items['viewCompare'] == '比选公告':
                        items['url'] = 'caigou.chinatelecom.com.cn/MSS-PORTAL/tenderannouncement/viewCompare.do?encryCode={}&id={}'.format(encryCode, article_id)
                    elif items['viewCompare'] == '单一来源采购公示':
                        items['url'] = self.single_source_url.format(encryCode, article_id)
                    else:
                        items['url'] = self.purchase_Notice_url.format(url_category, encryCode, article_id)

                elif items['category'] == '预审公告':
                    items['url'] = self.pre_check_url.format(article_id, encryCode)

                elif items['category'] == '采购公告澄清':
                    items['url'] = self.clearify_notice_url.format(article_id, encryCode)


                # 获取标题、采购公告、预审结果、以及澄清和结果都存在不同的xpath
                if items['category'] == '其他' or items['category'] == '采购公告澄清':
                    items['title'] = each_tr.xpath('./td[2]/a/text()').extract_first().strip()
                elif items['category'] == '采购公告':
                    items['title'] = each_tr.xpath('./td[3]/a/text()').extract_first().strip()
                # 预审公告
                else:
                    items['title'] = each_tr.xpath('./td[4]/a/text()').extract_first().strip()


                # 获取日期、采购公告、预审结果、以及澄清和结果都存在不同的xpath
                if items['category'] == '其他':
                    items['web_time'] = each_tr.xpath('./td[3]/text()').extract_first().split(' ')[0]

                elif items['category'] == '采购公告':
                    items['web_time'] = each_tr.xpath('./td[6]/text()').extract_first().split(' ')[0]

                elif items['category'] == '采购公告澄清':
                    items['web_time'] = each_tr.xpath('./td[4]/text()').extract_first().split(' ')[0]
                # 预审公告
                else:
                    items['web_time'] = each_tr.xpath('./td[7]/text()').extract_first().split(' ')[0]


                # 获取城市id
                try:
                    items['addr_id'] = self.city_dict[items['addr']]
                except:
                    for each_city in self.city_dict:
                        if each_city in items['title']:
                            items['addr_id'] = self.city_dict[each_city]
                            break

                if 'addr_id' not in items:
                    items['addr_id'] = '100'

                yield scrapy.Request(url='https://' + items['url'], callback=self.parse_article,
                                     meta={'items': deepcopy(items)})


        except Exception as e:
            print(items['url'])
            print(items['title'])
            print('标题日期链接获取失败')
            print(e)
            pass


    def parse_article(self, response):

        items = response.meta['items']
        # 系统时间，时间戳
        items["time"] = '%.0f' % time.time()
        # 分类id
        items["sheet_id"] = '29'
        # 文章来源
        items["source_name"] = '中国电信-阳光采购网外部门户'
        # 五位数的ID
        items["type_id"] = '38257'

        try:
            # 获取正文内容
            # 澄清公告中部分网页会出现网页被关闭 所以会出现no attribute name group的情况
            dirty_article = re.search(r'<div class="universal_two_content">(.*?)<iframe id="mainSubframe1"',
                                      response.text, re.S).group(1)
            # 利用正则清除垃圾数据
            # clean_article = re.sub(r'\r|\t|\n|<!--.*?-->|<input.*?>|class=[\'\"].*?[\'\"]|id=[\'\"].*?[\'\"]|style=[\'\"].*?[\'\"]|<STYLE.*?>.*?<\/STYLE>|class=\w*', ' ', dirty_article)
            # 将文章的垃圾数据进行清洗（新版）
            clean_article = re.sub(eval(self.regularExpression), ' ', dirty_article)
            # 保存正文信息
            items['intro'] = clean_article
            yield items

        except Exception as e:
            print(items['url'])
            print(items['title'])
            print('正文匹配出错')
            print(e)
            pass
