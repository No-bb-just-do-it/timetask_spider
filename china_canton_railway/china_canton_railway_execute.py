from scrapy.cmdline import execute
import os

# 中国铁路广州局集团有限公司物资采购商务平台
os.system('scrapy crawl china_canton_railway_spider')
# 中国中铁采购电子商务平台
os.system('scrapy crawl china_railway_luban_spider')