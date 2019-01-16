# -*- coding: utf-8 -*-

# from scrapy_redis.spiders import RedisSpider

from scrapy import Request, Spider
from copy import deepcopy
import re, time, logging


class GuangxiGovPurSpider(Spider):
    name = 'guangxi_gov_pur'
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
        self.half_detail_url = "http://www.ccgp-guangxi.gov.cn"
        self.part_url = "http://www.ccgp-guangxi.gov.cn/CmsNewsController/getCmsNewsList/"
        self.html5 = '<a href = {}>下载附件</a>'
        self.city_dict = {}
        # 将各个城市与编号制成字典
        # with open('城市编号id.txt', 'r', encoding='GB2312')as f:
        #     city_data = f.read()
        #     for each_info in city_data.split('\n'):
        #         self.city_dict[each_info.split(',')[0]] = each_info.split(',')[1]

        with open('/root/RegularExpression.txt', 'r')as f:
            self.regularExpression = f.read()

        self.category_dict = {
            # '公开招标公告': '38255',
            # '询价公告': '38255',
            # '竞争性谈判公告': '38255',
            # '单一来源': '38255',
            # '资格预审': '38255',
            # '邀请公告': '38255',
            # '其它公告': '38255',
            # '单一来源公告': '38255',
            # '资格预审公告': '38255',
            # '其他公告': '38255',
            # '竞争性磋商公告': '38255',
            # '中标公告': '38257',
            '中标结果': '38257',
            # '成交公告': '38257',
            # '废标流标': '38257',
            # '更正公告': '38256',
            # '终止公告': '38256',
            '招标公告':'38255',
            '招标更正':'38256'

        }
        self.start_urls = [
            # 成交公告
            ('中标结果', "channelCode-shengji_cjgg/param_bulletin/20/page_{}.html", 5),    # 区级
            ('中标结果', "channelCode-sxjcg_cjgg/param_bulletin/20/page_{}.html", 11),      #县级
            # 区级中标公告
            ('中标结果', 'channelCode-shengji_zbgg/param_bulletin/20/page_{}.html', 5),
            # 县级中标公告
            ('中标结果', 'channelCode-sxjcg_zbgg/param_bulletin/20/page_{}.html', 8),
            # 区级预公示
            ('招标公告', 'channelCode-shengji_zbwjygg/param_bulletin/20/page_{}.html', 3),
            # 县级预公示
            ('招标公告', 'channelCode-sxjcg_zbwjygs/param_bulletin/20/page_{}.html', 3),
            # 区级单一来源
            ('招标公告', 'channelCode-shengji_dylygg/param_bulletin/20/page_{}.html', 3),
            # 县级单一来源
            ('招标公告', 'channelCode-sxjcg_dylygg/param_bulletin/20/page_{}.html', 3),
            # 区级其它公告
            ('招标公告', 'channelCode-shengji_qtgg/param_bulletin/20/page_{}.html', 3),
            # 县级其它公告
            ('招标公告', 'channelCode-sxjcg_qtgg/param_bulletin/20/page_{}.html', 3),
            # 区级采购公告
            ('招标公告', 'channelCode-sxjcg_cggg/param_bulletin/20/page_{}.html', 5),
            # 县级采购公告
            ('招标公告', 'channelCode-shengji_cggg/param_bulletin/20/page_{}.html', 10),
            # 区级更改
            ('招标更正', 'channelCode-shengji_gzgg/param_bulletin/20/page_{}.html', 3),
            # 县级更改
            ('招标更正', 'channelCode-sxjcg_gzgg/param_bulletin/20/page_{}.html', 3),
        ]


    def start_requests(self):
        for urls_mes in self.start_urls:
            # 构造分页列表
            urls = [self.part_url + urls_mes[1].format(i) for i in range(1, urls_mes[2])]
            # urls = [self.part_url + urls_mes[1].format(i) for i in range(1, 5)]
            for url in urls:
                # print(url)
                items = {}
                items["type"] = urls_mes[0]
                try:
                    yield Request(url, headers=self.headers, callback=self.parse_list, meta={"items": deepcopy(items)})
                except Exception as e:
                    print("列表页错误", e, items['url'])
                    # logging.warning()
                    pass

    def parse_list(self, response):
        # 获取详情页列表
        try:
            items = response.meta["items"]
            # 获取列表页的所有li标签
            lis = response.xpath('//div[@class="column infoLink noBox unitWidth_x6"]//li')

            for li in lis:
                items["url"] = self.half_detail_url + li.xpath("./a/@href").extract_first()
                items["title"] = li.xpath("./a/@title").extract_first().strip()
                items["web_time"] = li.xpath('./span[@class="date"]/text()').extract_first()
                yield Request(items["url"], headers=self.headers, callback=self.detail_parse,
                              meta={"meta": deepcopy(items)})

        except Exception as e:
            print("获取详情列表页错误", e, items['url'])
            pass

    def detail_parse(self, response):
        # 获取详情
        items = response.meta["meta"]
        p_str = response.text
        try:
            items["type_id"] = self.category_dict[items["type"]]
            dirty_article = re.search(r'<div style="text-align:center;">(.*?)<h6>相关公告</h6>', p_str, re.S).group(1)
            #拼接附件html
            try:
                half_file_url = re.search(r'<h3>附件</h3>.*?<li><a href="(.*?)">.*?</a></li>').group(1)
            except:
                pass
            else:
                file_url = self.half_detail_url + half_file_url
                dirty_article = dirty_article + '\n'+self.html5.format(file_url)
            items["intro"] = re.sub(eval(self.regularExpression), ' ', dirty_article)
            items["time"] = int(time.time())
            # area = "广西"
            items["addr_id"] = 416
            items["source_name"] = "广西壮族自治区政府采购网"
            yield items

        except Exception as e:
            print("获取详情字段出错", e, items['url'])
            pass
