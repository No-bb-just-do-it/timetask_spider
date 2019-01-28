from utils.STMP import send_mail_when_error


class parse_url_title_time_class:

    def __init__(self, infos, items, xpath_rule, spider_name, base_url = ''):
        # 列表页的信息
        self.infos = infos
        self.items = items
        self.xpath_rule = xpath_rule
        self.spider_name = spider_name
        self.base_url = base_url
        self.error_count = 0

    def parse(self):
        for each_li in self.infos:
            self.items['title'] = ''
            self.items['url'] = ''
            self.items['web_time'] = ''
            self.items['intro'] = ''
            self.items['addr_id'] = ''

            try:
                self.items['title'] = each_li.xpath(self.title_rule).extract_first().strip()
            except:
                pass

            try:
                self.items['url'] = self.base_url + each_li.xpath(self.url_rule).extract_first()
            except:
                msg = self.spider_name + ', 该爬虫详情页获取url失败'
                send_mail_when_error(msg)
                self.error_count += 1
                if self.error_count > 3:
                    quit()
                    msg = self.spider_name + ', 该爬虫因详情页获取失败被暂停'
                    send_mail_when_error(msg)
                pass

            try:
                self.items['web_time'] = each_li.xpath(self.web_time_rule).extract_first().strip()
            except:
                pass

            yield self.items