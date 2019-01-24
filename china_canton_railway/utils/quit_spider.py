from scrapy.exceptions import CloseSpider

def quit():
    raise CloseSpider('close spider')