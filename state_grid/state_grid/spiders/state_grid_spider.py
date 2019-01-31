# -*- coding: utf-8 -*-
import re
import time
from copy import deepcopy
import scrapy


class StateGridSpiderSpider(scrapy.Spider):
    name = 'state_grid_spider'
    allowed_domains = ['sgcc.com.cn']
    # start_urls = ['http://sgcc.com.cn/']

    def __init__(self):

        self.city_dict = {}
        # 将各个城市与编号制成字典
        with open('城市编号id.txt', 'r', encoding='GB2312')as f:
            city_data = f.read()
            for each_info in city_data.split('\n'):
                self.city_dict[each_info.split(',')[0]] = each_info.split(',')[1]

        # 下载标签 往后会将其拼接到items['intro']中
        self.download_html_tag = '<h4><a href={}>下载招标公告文件请点击这里</a></h4>'
        # 招标文件下载链接 使用长id来拼接
        self.bid_download_link = 'http://ecp.sgcc.com.cn/structData/{}.zip'

        # 招标公告列表页链接
        self.bidding_Notice_url = 'http://ecp.sgcc.com.cn/topic_project_list.jsp?columnName=topic10&site=global&company_id=&status=&project_name=&pageNo={}'
        # 招标结果列表链接
        self.result_Notice_url = 'http://ecp.sgcc.com.cn/topic_news_list.jsp?columnName=topic23&site=global&company_id=&column_code1=014001007&column_code2=014002003&pageNo={}'
        # 中标候选人列表页链接
        self.candidate_Notice_url = 'http://ecp.sgcc.com.cn/topic_news_list.jsp?columnName=topic22&site=global&company_id=&column_code1=014001003&column_code2=014002009&pageNo={}'
        # 竞争者公告列表页链接
        self.competition_url = 'http://ecp.sgcc.com.cn/topic_announcement_list.jsp?columnName=topic40&site=global&column_code=019001&company_id=&pageNo={}'

        # 构造正文文章链接地址（招标公告）
        self.bidding_Notice_article_url = 'http://ecp.sgcc.com.cn/html/project/{}/{}.html'
        # 构造正文文章链接地址（招标结果）
        self.result_Notice_article_url = 'http://ecp.sgcc.com.cn/html/news/{}/{}.html'
        # 构造正文文章链接地址（中标候选人公示）
        self.candidate_Notice_article_url = 'http://ecp.sgcc.com.cn/html/news/{}/{}.html'
        # 构造正文文章链接地址（竞价公告）
        self.competition_article_url = 'http://ecp.sgcc.com.cn/html/announcement/{}.html'


    def start_requests(self):
        # 招标公告 共481页 每天数据跨度约1页
        for page in range(1, 3):
            items = {}
            items['type_id'] = '38255'
            items['download_file'] = 1
            url = self.bidding_Notice_url.format(page)
            yield scrapy.Request(url = url, callback = self.parse_bidding_Notice, meta = {'items' : deepcopy(items)}, dont_filter = True)

        # 招标结果 共627页 每天数据跨度约1页
        for page in range(1, 3):
            items = {}
            items['type_id'] = '38257'
            url = self.result_Notice_url.format(page)
            yield scrapy.Request(url=url, callback=self.parse_result_Notice, meta={'items': deepcopy(items)}, , dont_filter = True)

        # 中标候选人公示 共382页 每天数据跨度约1页
        for page in range(1, 3):
            items = {}
            items['type_id'] = '38257'
            url = self.candidate_Notice_url.format(page)
            yield scrapy.Request(url=url, callback=self.parse_result_Notice, meta={'items': deepcopy(items)}, , dont_filter = True)

        # 竞价公告 共101页 每天数据跨度约1页
        for page in range(1, 3):
            items = {}
            items['competition'] = 1
            items['type_id'] = '38255'
            url = self.competition_url.format(page)
            yield scrapy.Request(url=url, callback=self.parse_result_Notice, meta={'items': deepcopy(items)}, , dont_filter = True)


    # 列表页为tr、td标签
    def parse_bidding_Notice(self, response):
        items = response.meta['items']
        # 获取所有的tr标签、标题内容都在里面、由于第一个是标题字段、所有从第二个开始才是招标信息
        all_trs = response.xpath('//table[@class="font02"]/tr')[1:]
        # 遍历所有tr标签从中获取数据
        for each_tr in all_trs:
            items['title'] = each_tr.xpath('./td[3]/a/@title').extract_first().strip()
            for city in self.city_dict:
                if city in items['title']:
                    items['addr_id'] = self.city_dict[city]
                    break

            if 'addr_id' not in items:
                items['addr_id'] = '100'

            items['web_time'] = each_tr.xpath('./td[4]/text()').extract_first().strip()
            # 首先获取到tr标签中文章id的信息、然后通过正则提取id、并且构造出文章url链接
            article_id = each_tr.xpath('./td[3]/a/@onclick').extract_first()
            short_one = re.search(r"showProjectDetail\('(\d*?)','(\d*?)'\);", article_id, re.S).group(1)
            long_one = re.search(r"showProjectDetail\('(\d*?)','(\d*?)'\);", article_id, re.S).group(2)

            # 由于只有招标公告存在下载文件、所以添加一个判断语句
            if 'download_file' in items:
                # 通过长id来构造下载文件的url
                items['file_link'] = self.bid_download_link.format(str(long_one)[1:])

            # 通过长id以及短id拼接正文的url
            items['url'] = self.bidding_Notice_article_url.format(short_one, long_one)

            yield scrapy.Request(url = items['url'], callback = self.parse_article, meta = {'items' : deepcopy(items)})


    # 列表页为ul、li标签
    def parse_result_Notice(self, response):
        items = response.meta['items']
        all_lis = response.xpath('//div[@class="titleList"]/ul/li')

        # 遍历所有li标签从中获取数据
        for each_li in all_lis:
            # 首先获取标题、以及从标题中获取城市id
            items['title'] = each_li.xpath('./div[@class="titleList_01"]/a/@title').extract_first().strip()
            for city in self.city_dict:
                if city in items['title']:
                    items['addr_id'] = self.city_dict[city]
                    break

            if 'addr_id' not in items:
                items['addr_id'] = '100'

            # 获取日期以及文章链接
            items['web_time'] = each_li.xpath('./div[@class="titleList_02"]/text()').extract_first().strip()

            # 首先获取到tr标签中文章id的信息、然后通过正则提取id、并且构造出文章url链接
            article_id = each_li.xpath('./div[@class="titleList_01"]/a/@onclick').extract_first()
            if items['type_id'] != '38255':
                # 获取构造url所需的id(结果公告、中标人候选公示)
                long_one = re.search(r"showNewsDetail\( '(\d*?)', '(\d*?)'\);", article_id, re.S).group(1)
                short_one = re.search(r"showNewsDetail\( '(\d*?)', '(\d*?)'\);", article_id, re.S).group(2)

                # 通过长id以及短id拼接正文的url 招标结果的文章链接id为先长后短
                # 由于结果公告与中标候选人公告的文章构造方法一摸一样、所以可以公用同一段代码来构造url
                items['url'] = self.result_Notice_article_url.format(long_one, short_one)
                # 打印原文链接测试是否有效
                # print(items['url'])

            else:
                # 获取构造url所需的id（竞价公告）、由于获取规则不一样、所以使用判断语句分开写
                long_one = re.search(r"showAnnounceDetail\('(.*?)'\);", article_id, re.S).group(1)
                items['url'] = self.competition_article_url.format(long_one)


            yield scrapy.Request(url = items['url'], callback = self.parse_article, meta = {'items' : deepcopy(items)})



    def parse_article(self, response):
        items = response.meta['items']

        # 除了竞价公告的文章匹配规则不一样、其余4样全部采用下列的第一种正则匹配规则
        if 'competition' not in items:
            dirty_article = re.search(
            r'<div class="articleTitle font04" style="height: 63px;">(.*?)<div class="articleFoot">', response.text,
            re.S).group(1)
        else:
            dirty_article = re.search(
            r'<!-- 竞价公告正文开始 -->(.*?)<!--EndFragment-->', response.text, re.S
            ).group(1)

        # 除了招标公告正文中存在下载附件链接、所有判断为True的需要构造下载附件的链接、其余的公告不存在下载附件、所以可以正常处理
        if 'download_file' in items:
            clean_article = re.sub(r'\n|\t|\r', '', dirty_article) + self.download_html_tag.format(items['file_link'])
        else:
            clean_article = re.sub(r'\n|\t|\r', '', dirty_article)

        items["time"] = '%.0f' % time.time()
        items["sheet_id"] = '29'
        items["source_name"] = '国家电网公司电子商务平台'
        items['intro'] = clean_article

        yield items
