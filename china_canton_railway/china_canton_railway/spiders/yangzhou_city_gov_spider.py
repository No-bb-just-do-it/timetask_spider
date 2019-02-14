# -*- coding: utf-8 -*-
from .common_spider import CommonSpider
from utils.Regular_Expression import category

# http://zfcg.yangzhou.gov.cn/ @ 扬州市政府采购网
class yangzhouSpiderSpider(CommonSpider):
    name = 'yangzhou_city_gov_spider'

    def __init__(self):

        self.baseUrl = ''
        self.error_count = 0
        self.source_name = '扬州市政府采购网'
        self.addr_id = '400'
        self.category = category

        self.xpath_rule = {
            'list_page' : '//div[@class="cont mt10"]/ul/li',
            'title_rule': './/a/text()',
            'url_rule': './/a/@href',
            'web_time_rule': './/span/text()',
            'content_rule' : r'<div class="content" id="zoom">(.*?)<!-- bottom begin-->'
        }

        self.headers = {
            'Host': 'zfcg.yangzhou.gov.cn',
            'Connection': 'keep-alive'
        }

        self.start_urls = [
            # 市县级 采购公告604 每天1页 结果公告400 每天1页
            ('招标公告', 'http://zfcg.yangzhou.gov.cn/qtyy/zfcgw/xsq_list.jsp?currentPage={}&channel_id=4749b63313a040b7bd17119f43f19307', 3),
            ('招标结果', 'http://zfcg.yangzhou.gov.cn/qtyy/zfcgw/xsq_list.jsp?currentPage={}&channel_id=781558110dac4d5a96083bb1bd49d0a3', 3),
            # 市级 采购公告 公开招标80 单一来源20 竞争性磋商3 每天更新均1页
            ('招标公告', 'http://zfcg.yangzhou.gov.cn/qtyy/zfcgw/ggzyjyzx_front_cggg_common_list.jsp?currentPage={}&channel_id=0fa7f17644ef4b368d27a1e7a922a7fb', 3),
            ('招标公告', 'http://zfcg.yangzhou.gov.cn/qtyy/zfcgw/ggzyjyzx_front_cggg_common_list.jsp?currentPage={}&channel_id=c296b4620dc3421b92ac357e89304080', 3),
            ('招标公告', 'http://zfcg.yangzhou.gov.cn/qtyy/zfcgw/ggzyjyzx_front_cggg_common_list.jsp?currentPage={}&channel_id=bdecff5f514d4551875464b86ce430ae', 3),
            # 市级 成交公告 公开招标57 单一来源9 竞争性谈判22 每天更新均1页
            ('招标结果', 'http://zfcg.yangzhou.gov.cn/qtyy/zfcgw/ggzyjyzx_front_cjgg_common_list.jsp?currentPage={}&channel_id=126cba7e082642f094045c13bac8ef1e', 3),
            ('招标结果', 'http://zfcg.yangzhou.gov.cn/qtyy/zfcgw/ggzyjyzx_front_cjgg_common_list.jsp?currentPage={}&channel_id=3cd74d79b720401e96847b42c4aeb438', 3),
            ('招标结果', 'http://zfcg.yangzhou.gov.cn/qtyy/zfcgw/ggzyjyzx_front_cjgg_common_list.jsp?currentPage={}&channel_id=fca5c4ee19e142cdb28695fe73936ffc', 3),
            ('招标结果', 'http://zfcg.yangzhou.gov.cn/qtyy/zfcgw/ggzyjyzx_front_cjgg_common_list.jsp?currentPage={}&channel_id=242897320e264736bd37208795580743', 3),
        ]