import random
import redis
from scrapy import signals
from scrapy.exceptions import IgnoreRequest
from .settings import redis_ip
from .settings import USER_AGENT_LIST

class RandomUserAgent:

    def process_request(self, request, spider):
        UA = random.choice(USER_AGENT_LIST)
        request.headers['User-Agent'] = UA


class RandomIpMiddleWare(object):

    def process_request(self, request, spider):
        # 从列表中获取ip
        ip_pool = redis_ip.lindex("ip_pool", 0)
        # ip_pool = '175.167.22.29:35771'

        # 获取请求的协议头是http还是https，根据该请求头使用相应的代理ip
        HTTP = request.url.split('://')[0]
        if HTTP == 'http':
            # ip = 'http://' + random.choice(ip_pool).decode('utf-8')
            ip = 'http://' + ip_pool.decode('utf-8')
            request.meta['proxy'] = ip
            # print(ip)
        else:
            # ip = 'https://' + random.choice(ip_pool).decode('utf-8')
            ip = 'https://' + ip_pool.decode('utf-8')
            request.meta['proxy'] = ip
            # print(ip)