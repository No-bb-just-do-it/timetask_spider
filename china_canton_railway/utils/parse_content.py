from utils.Regular_Expression import regularExpression, regularExpression02
import re

class Parse_content:

    def get_clean_content(self, article_rule, regularExpression, regularExpression02, dirty_content):
        dirty_article = re.search(article_rule, dirty_content.text, re.S).group(1)
        dirty_article = re.sub(regularExpression02, '>', dirty_article)
        clean_article = re.sub(regularExpression, ' ', dirty_article)
        return clean_article


pc = Parse_content()