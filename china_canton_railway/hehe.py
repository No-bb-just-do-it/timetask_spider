import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
                  ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'
}


def get_detail(url):
    res = requests.get(url).json()
    for item in res['data']['poi_list']:
        data = dict()
        data['add'] = ''
        data['name'] = ''
        data['tel'] = ''
        for i in item['domain_list']:
            try:
                if i.get('id') == '1010':
                    data['add'] = i['value']
            except:
                pass
            try:
                if i.get('id') == '2001':
                    data['name'] = i['value']
            except:
                pass
            try:
                if i.get('id') == '2004' and i.get('action') == 'tel':
                        data['tel'] = i['value']
            except:
                pass
        print(data)


def main():
    url = 'https://www.amap.com/service/poiInfo?query_type=TQUERY&pagesize=20&pagenum={}&qii=true&cluster_state=5&need_utd=true&utd_sceneid=400002&div=PC1000&addr_poi_merge=true&is_classify=true&zoom=4&city=440100&keywords=喜茶'
    for page in range(1, 10000):
        try:
            each_url = url.format(page)
            get_detail(each_url)
        except:
            break


if __name__ == '__main__':
    main()



