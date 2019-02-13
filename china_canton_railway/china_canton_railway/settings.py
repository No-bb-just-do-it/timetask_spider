# -*- coding: utf-8 -*-
import redis
from spider_name import spiders_name


BOT_NAME = 'china_canton_railway'

SPIDER_MODULES = ['china_canton_railway.spiders']
NEWSPIDER_MODULE = 'china_canton_railway.spiders'

# command设置
COMMANDS_MODULE = 'china_canton_railway.commands'

# 输入爬取的网站
GOING_TO_CRAWL = [each_spider[0] for each_spider in spiders_name.items()]

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32


DOWNLOAD_DELAY = 0.3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 1
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
	'Connection': 'keep-alive',
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36'
}


# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'china_canton_railway.middlewares.ChinaCantonRailwaySpiderMiddleware': 543,
#}


DOWNLOADER_MIDDLEWARES = {
   'china_canton_railway.middlewares.RandomUserAgent': 543,
   # 'china_canton_railway.middlewares.RandomIpMiddleWare': 555,
}


ITEM_PIPELINES = {
   'china_canton_railway.pipelines.UniversalPipeline': 300,
    # 'scrapy_redis.pipelines.RedisPipeline': 400,
}


USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.2)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:62.0) Gecko/20100101 Firefox/62.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'
]

# DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# # 用于配置调度器是否需要持久化
# # 如果为True, 当程序结束了, 依然会保留Redis中的指纹和待爬的请求
# # 如果为False, 当程序结束了, 依然会请空Redis中的指纹和待爬的请求
# SCHEDULER_PERSIST = True
# # Redis数据库配置
# REDIS_URL = "redis://120.79.14.9:6379/10"

# 链接ip池
pool = redis.ConnectionPool(host='120.77.159.174', port=6379, db=6)
redis_ip = redis.Redis(connection_pool = pool)
