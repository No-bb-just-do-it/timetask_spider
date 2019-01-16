# -*- coding: utf-8 -*-
import logging
import re
import time
from copy import deepcopy
from scrapy.exceptions import CloseSpider
from STMP import send_mail_when_error
import scrapy


class MiitComprehensiveSpider(scrapy.Spider):
    name = 'MIIT_comprehensive'
    allowed_domains = ['miit.gov.cn']

    def __init__(self):
        # 爬虫名
        self.spider_name = 'MIIT_comprehensive'

        self.city_dict = {}
        # 将各个城市与编号制成字典
        with open('城市编号id.txt', 'r', encoding='GB2312')as f:
            city_data = f.read()
            for each_info in city_data.split('\n'):
                self.city_dict[each_info.split(',')[0]] = each_info.split(',')[1]

        with open('/root/RegularExpression.txt', 'r')as f:
                self.regularExpression = f.read()

        self.pattern01 = r'地\s*址：(.*?)</p>'
        self.pattern_list = [self.pattern01]

        # 各种类列表页的post_url
        self.url = 'http://txzb.miit.gov.cn/DispatchAction.do?reg=denglu&pagesize=11'

        # 招标公告/资格预审公告/招标终止公告
        self.bid_Notice_url = 'http://txzb.miit.gov.cn/DispatchAction.do?reg=denglu&pagesize=11&page={}&efFormEname=POIX14'
        # 中标候选人公示
        self.bid_dealNotice_url = 'http://txzb.miit.gov.cn/DispatchAction.do?reg=denglu&pagesize=11&methodName=queryZhongbiao&page={}&efFormEname=POIX62'
        # 中标业绩信息
        self.bid_dealNotice_infos_url = 'http://txzb.miit.gov.cn/DispatchAction.do?reg=denglu&pagesize=11&page={}&efFormEname=POIX61'

        # 用于文章拼接的url
        self.base_url = 'http://txzb.miit.gov.cn'

    def start_requests(self):
        # 招标公告/资格预审公告/招标终止公告 共6563页 每天跨度10~15页
        for page in range(1, 21):
            items = {}
            items['type_id'] = '38255'
            items['Notice'] = 'bid_notice'
            yield scrapy.Request(
                url = self.bid_Notice_url.format(str(page)), callback = self.parse, meta = {'items' : deepcopy(items)}, dont_filter=True
            )

        # 中标候选人公示 共3636页 每天跨度7~10页
        for page in range(1, 15):
            items = {}
            items['type_id'] = '38257'
            items['Notice'] = 'candidate'
            yield scrapy.Request(
                url=self.bid_dealNotice_url.format(str(page)), callback = self.parse, meta = {'items': deepcopy(items)}, dont_filter=True
            )

        # 中标业绩信息 共807页 跨度无法预测 大概10页左右  因为日期是乱序的
        for page in range(1, 21):
            items = {}
            items['type_id'] = '38257'
            items['Notice'] = 'deal_notice'
            yield scrapy.Request(
                url = self.bid_dealNotice_infos_url.format(str(page)), callback = self.parse, meta = {'items' : deepcopy(items)}, dont_filter=True
            )

    # 解析列表页代码
    def parse(self, response):
        try:
            items = response.meta['items']

            # 获取候选人和招标信息的table标签
            if items['Notice'] == 'candidate' or items['Notice'] == 'bid_notice':
                all_trs = response.xpath('//form[@id="queryFrm"]/child::table')[2]
            # 中标信息的列表table被多一层div包着 所以要额外使用判断
            else:
                all_trs = response.xpath('//form[@id="queryFrm"]/child::div')[0]

            # 因为中标业绩form标签下的第三个不是table标签 而是 div 所以要另行判断
            if 'div' in str(all_trs):
                all_trs = all_trs.xpath('.//table')

            for each_tr in all_trs.xpath('.//tr'):
                # 包含着标题与日期、需要用分隔符分开
                bid_infos = each_tr.xpath('.//td[@class="STYLE1"]/a/text()').extract_first().rsplit(' ', 1)
                # 获取标题有时候会出现垃圾字符, 进行清洗
                title = bid_infos[0].replace('\xa0', '').rsplit(' ', 1)[0].strip()

                # 在公告列表有可能出现 终止公告的信息  并且 web_time = '\xa0\xa0\xa0'  所以需要增加一层判断
                if '终止公告' in title or items['Notice'] == 'candidate' or items['Notice'] == 'deal_notice' or items['Notice'] == 'bid_notice':
                    title = re.sub(r'\t|\r|\n', '', title)

                items['title'] = title
                items['web_time'] = bid_infos[-1]
                link = each_tr.xpath('.//td[@class="STYLE1"]//a/@href').extract_first()
                items['url'] = self.base_url + re.search(r"javascript:locationForwardClick\('(.*?)'\)", link).group(1)

                yield scrapy.Request(url = items['url'], callback = self.parse_article, meta = {'items' : deepcopy(items)})

        except Exception as e:
            print(items['url'])
            print(items['title'])
            print('标题日期链接获取失败')
            print(e)
            pass


    def parse_article(self, response):
        try:
            items = response.meta['items']
            # 获取文章的源代码
            dirty_article = response.text
            # 因为招标失败的公告会出现日期是\xa0\xa0\xa0的情况  只针对招标公告，我们在文本内容进行提取, 先进行判断
            if '\xa0' in items['web_time']:
                # 由于招标失败的公告无法在列表页获取日期、所以只能在正文中使用正则获取日期
                date = re.search(r'发布日期：(.*?)\s', dirty_article).group(1)
                items['web_time'] = date
                # 由于标题是 终止公告 所以使用38257
                items['type_id'] = '38257'

            # 招标公告/资格预审公告/招标终止公告使用该正则
            if items['Notice'] == 'bid_notice':
                try:
                    dirty_article = re.search(r'<tr height="30px" class="tableRow1">(.*?)<!--', dirty_article, re.S).group(1)
                except:
                    dirty_article = re.search(r'<tr height="30px" class="tableRow1">(.*?)</html>', dirty_article, re.S).group(1)

            # 候选人公示使用该正则
            elif items['Notice'] == 'condidate':
                dirty_article = re.search(r'<!--DWLayoutTable-->(.*?)</html>', dirty_article, re.S).group(1)

            # 中标公告使用该正则
            elif items['Notice'] == 'deal_notice':
                dirty_article = re.search(r'<link href="./EF/Images/tab.css" rel="stylesheet" type="text/css"/>(.*?)</html>', dirty_article, re.S).group(1)
            # 进行简单的数据清洗
            clean_article = re.sub(eval(self.regularExpression), ' ', dirty_article)

            # 遍历城市字典 通过标题获取addr信息
            for each_city in self.city_dict:
                if each_city in items['title']:
                    items['addr_id'] = self.city_dict[each_city]
                    break

            # 如果不能通过标题获取addr 则使用正则从正文中通过一些re表达式获取
            if 'addr' not in items:
                # 遍历一次正则模式
                for each_pattern in self.pattern_list:
                    try:
                        addr = re.search(each_pattern, dirty_article, re.S).group(1)
                    except:
                        continue
                    else:
                        # 通过匹配到的字符串 遍历城市列表 进行匹配
                        for each_city in self.city_dict:
                            if each_city in addr:
                                items['addr_id'] = self.city_dict[each_city]
                                break
                    break

            # 如果经常两层判断依然没有结果、则使用默认值全国
            if 'addr_id' not in items:
                items['addr_id'] = '100'

            # 系统时间，时间戳
            items["time"] = '%.0f' % time.time()
            # 分类id
            items["sheet_id"] = '29'
            # 文章来源
            items["source_name"] = '工信部通信工程建设项目招标投标管理信息平台'
            # 文章信息
            items['intro'] = clean_article
            # print(items)
            yield(items)

        except Exception as e:
            print(items['url'])
            print(items['title'])
            print('标题日期链接获取失败')
            print(e)
            pass
