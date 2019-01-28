from utils.city_data import get_city_dict
from utils.Regular_Expression import regularExpression, regularExpression02, category
import re

class parse_content_class:

    def __init__(self, items, response, content_rule, source_name):
        self.items = items
        self.response = response
        self.content_url = content_rule
        self.source_name = source_name
        self.city_data = get_city_dict()

    def parse_content(self):
        try:
            dirty_article = re.search(self.content_url, self.response.text, re.S).group(1)
            dirty_article = re.sub(regularExpression02, '>', dirty_article)
            clean_article = re.sub(regularExpression, ' ', dirty_article)
            self.items['intro'] = clean_article
        except:
            pass

        if '更正' in self.items['title'] or '变更' in self.items['title']:
            self.items['type_id'] = '38256'

        if self.items['addr_id'] == '':
            for city in self.city_data:
                if city in self.items['title']:
                    self.items['addr_id'] = self.city_data[city]
                    break

        self.items["source_name"] = self.source_name

        yield self.items