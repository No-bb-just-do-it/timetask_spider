from scrapy.cmdline import execute

spiders = [
	'scrapy|crawlall',
]

if __name__ == '__main__':
	for spider in spiders:
		execute(spider.split('|'))