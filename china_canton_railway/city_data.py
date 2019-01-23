

def get_city_dict():
    city_dict = {}
    # 将各个城市与编号制成字典
    with open('城市编号id.txt', 'r', encoding='GB2312')as f:
        city_data = f.read()
        for each_info in city_data.split('\n'):
            city_dict[each_info.split(',')[0]] = each_info.split(',')[1]

    return city_dict