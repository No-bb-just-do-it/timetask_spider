# -*- coding: utf-8 -*-

# Scrapy settings for guangxi_gov_purchase project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import datetime

import redis
from fake_useragent import UserAgent

BOT_NAME = 'guangxi_gov_purchase'

SPIDER_MODULES = ['guangxi_gov_purchase.spiders']
NEWSPIDER_MODULE = 'guangxi_gov_purchase.spiders'

# 添加日志
# today = datetime.datetime.now()
# log_file_path = "log/{}_{}_{}.log".format(today.year, today.month, today.day)
#
# LOG_LEVEL = "WARNING"
# LOG_FILE = log_file_path

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'guangxi_gov_purchase (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.2
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 10
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
    'Host': 'www.ccgp-guangxi.gov.cn'
}
ua = UserAgent()

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'guangxi_gov_purchase.middlewares.GuangxiGovPurchaseSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'guangxi_gov_purchase.middlewares.RandomUseagent': 543,
    'guangxi_gov_purchase.middlewares.RandomIpMiddleWares': 555,

}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'guangxi_gov_purchase.pipelines.GuangxiGovPurchasePipeline': 300,
    'scrapy_redis.pipelines.RedisPipeline': 400,
}
#
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Request去重的类
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# 调度器
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# 是否持久化存储
SCHEDULER_PERSIST = True
# 配置Redis数据库链接,url去重，放start_urls
REDIS_URL = 'redis://120.79.14.9:6379/4'

#获取代理ip
pool = redis.ConnectionPool(host="120.77.159.174", port=6379, db=6)
redis_ip = redis.Redis(connection_pool = pool)