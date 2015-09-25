# -*- coding: utf-8 -*-

import logging
from scrapy import signals
from scrapy.exceptions import NotConfigured

logger = logging.getLogger(__name__)

class NewsStat(object):
    def __init__(self, stats, url_save_path):
        self.stats = stats
        self.url_save_path = url_save_path

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('NEWS_STAT_ENABLED'):
            raise NotConfigured
        url_save_path = crawler.settings.get("NEWS_STAT_SCRAPED_URL_SAVE_PATH", "data/scraped_urls.txt")
        ext = cls(crawler.stats, url_save_path)
        crawler.signals.connect(ext.spider_opened, signal = signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal = signals.spider_closed)
        #crawler.signals.connect(ext.item_scraped, signal = signals.item_scraped)
        return ext

    def spider_opened(self, spider):
        logger.info("spider opened %s", spider.name)
        self.stats.set_value("scraped_urls", [])

    def spider_closed(self, spider):
        logger.info("spider closed %s", spider.name)
        scraped_urls = self.stats.get_value("scraped_urls")
        with open(self.url_save_path, "w") as fo:
            fo.write("\n".join(scraped_urls))

    def item_scraped(self, item, spider):
        logger.info("item scraped %s", item["title"])
