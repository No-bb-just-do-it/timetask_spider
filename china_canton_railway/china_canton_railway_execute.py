# from scrapy.cmdline import execute
import os
import time
from spider_name import spiders_name
from utils.STMP import send_mail_when_error

for each_spider in spiders_name.items():
    try:
        os.system('scrapy crawl {}'.format(each_spider[0]))
    except:
        msg = '该爬虫出错 : ', + each_spider[1]
        send_mail_when_error(msg)
        continue
    finally:
        time.sleep(0.2)


# for each_spider in spiders_name.items():
#     os.system('scrapy crawl {}'.format(each_spider[0]))
#     time.sleep(0.2)