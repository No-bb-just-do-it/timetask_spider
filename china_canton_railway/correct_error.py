import re

import requests
import pymysql

headers = {
        'Host': 'zwgk.hefei.gov.cn',
        'Referer': 'http://zwgk.hefei.gov.cn/zwgk/public/index.xp?doAction=zdlylist2&type=5&id=001000180002',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36'
        }

r = requests.get('http://zwgk.hefei.gov.cn/zwgk/public/spage.xp?doAction=view&indexno=667938726/201802-00052', headers = headers).content.decode('gbk')

dirty_article = re.search(r'style="font-weight:bold;">(.*?)<!-- GWD SHARE BEGIN 文章底部-->', r, re.S).group(1)
print(dirty_article)