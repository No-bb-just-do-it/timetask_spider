# -*- coding: utf-8 -*-

# from scrapy_redis.spiders import RedisSpider

from scrapy import Request, Spider
import requests
from copy import deepcopy
import re, time, logging


class GuangiGovPurSpider(Spider):
    name = 'guangxi_test'

    allowed_domains = ['ccgp-guangxi.gov.cn']

    # redis_key = 'liuzhouCategory:start_urls'
    def __init__(self):
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Host': 'www.ccgp-guangxi.gov.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        }
        self.start_url = "http://www.ccgp-guangxi.gov.cn/CmsNewsController/getCmsNewsList/channelCode-shengji_cggg/param_bulletin/20/page_1.html"
        # 需要补全的url
        self.dom_url = "http://www.ccgp-guangxi.gov.cn"
        # type_id分类
        self.type_id = {
            "采购公告": 38255,
            "单一来源公告": 38255,
            "其他公告": 38255,
            "招标文件预公示": 38255,
            "成交公告": 38257,
            "中标公告": 38257,
            "更正公告": 38256
        }

        self.html5 = '<a href = {}>下载附件</a>'

    def request_get(self, url):
        source = requests.get(url, headers=self.headers).content.decode()
        return source

    def start_requests(self):
        # 获取大标题信息
        try:
            source_page = self.request_get(self.start_url)
            parent_lis = re.findall(r'<li><a href="(.*?)" target="_self" title="(.*?)">.*?</a></li>', source_page)
            for parents_param in parent_lis:

                parent_url = self.dom_url + parents_param[0]
                # con = self.request_get(parent_url)

                # 获取分类总页数，并构列表页url
                # page_num = re.search(r'页次：1/(\d+)页</span>', con).group(1)
                model_url = re.sub(r'_1.html', '_{}.html', parent_url)
                children_url_lis = [model_url.format(i) for i in range(1, 21)]

                # 请求列表页
                items = {}
                for children_url in children_url_lis:
                    items['type_id'] = self.type_id[parents_param[1]]
                    yield Request(url=children_url, callback=self.get_detail_lis, headers=self.headers,
                                  meta={'items': deepcopy(items)}, dont_filter=True)
        except Exception as e:
            print("大标题页错误", e)
            # logging.warning()
            pass

    # 获取列表页详情url
    def get_detail_lis(self, response):
        try:
            items = response.meta['items']
            lis = response.xpath('//div[@class="column infoLink noBox unitWidth_x6"]//li')
            for li in lis:
                items["url"] = self.dom_url + li.xpath("./a/@href").extract_first()
                items["title"] = li.xpath("./a/@title").extract_first()
                dirty_time = li.xpath('./span[@class="date"]/text()').extract_first()
                # 转花为时间戳
                items["web_time"] = int(time.mktime(time.strptime(dirty_time, "%Y-%m-%d")))
                yield Request(items["url"], headers=self.headers, callback=self.detail_parse,
                              meta={"meta": deepcopy(items)})
        except Exception as e:
            print("列表页错误", e, items['url'])
            # logging.warning()
            pass

    # 获取详情页数据
    def detail_parse(self, response):

        items = response.meta["meta"]
        p_str = response.text
        try:
            dirty_page = re.search(r'<div class="frameReport">(.*?)<div id="a">', p_str, re.S).group(1)
            # 拼接附件html
            try:
                half_file_url = re.search(r'<h3>附件</h3>.*?<li><a href="(.*?)">.*?</a></li>').group(1)
            except Exception as e:
                pass
            else:
                file_url = self.dom_url + half_file_url
                dirty_page = dirty_page + '\n' + self.html5.format(file_url)
            items["intro"] = re.sub('[\n|\t|\r]', '', dirty_page)
            items["time"] = int(time.time())
            # area = "广西"
            items["addr_id"] = "416"
            items["source_name"] = "广西壮族自治区政府采购网"
            yield items
        except Exception as e:
            print("转pipline问题", e, items["url"])
