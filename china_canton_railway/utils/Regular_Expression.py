regularExpression = r'\r|\t|\n|<!--.*?-->|<input.*?>|id=[\'\"].*?[\'\"]|style=[\'\"].*?[\'\"]|<STYLE.*?</STYLE>|class=[\'\"].*?[\'\"]|class\s*\'*\"*=\s*[a-zA-Z0-9_]*\'*\"*|<style.*?>.*?<\/style>|<script.*?</script>|<style.*?</style>|lang=[\'\"].*?[\'\"]|name=[\'\"].*?[\'\"]|<meta.*?>'

# 眉山市
regularExpression02 = r'style=[\'\"].*?>'


category = {
            '招标公告' : '38255',
            '招标结果' : '38257',
            '变更公告' : '38256'
        }