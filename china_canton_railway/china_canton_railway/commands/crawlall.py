from scrapy.commands import ScrapyCommand
from china_canton_railway.settings import GOING_TO_CRAWL


class Command(ScrapyCommand):
    requires_project = True

    def syntax(self):
        return '[option]'

    def short_desc(self):
        return 'Runs all of the spiders'

    def run(self, arg, args):
        spider_list = self.crawler_process.spiders.list()
        for name in spider_list:
            if name not in GOING_TO_CRAWL:
                continue
            self.crawler_process.crawl(name)
        self.crawler_process.start()