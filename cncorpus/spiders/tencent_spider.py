# -*- coding: utf-8 -*-
import re
import scrapy
import logging
from cncorpus.items import NewsItem

logger = logging.getLogger(__name__)

class TencentSpider(scrapy.Spider):
    """
        腾讯新闻爬虫
    """
    name = "tencent"
    allowed_domains = ["qq.com"]
    start_urls = [
        "http://www.qq.com/"
    ]
    custom_settings = {
        "CORPUS_SAVE_PATH": "data/tencent.txt",
        "MAX_SCRAPE_URLS": 100000
    }

    def parse(self, response):
        return self.issue_new_request(response)

    def issue_new_request(self, response):
        for url in response.xpath("//div[@class='navBetaInner']//a/@href").extract():
            url = response.urljoin(url)
            if not self.is_in_scraped_urls(url) and not self.should_stop():
                logger.info("crawling " + url)
                self.add_to_scraped_urls(url)
                yield scrapy.Request(url, callback = self.issue_new_request)
        for url in response.xpath("//a/@href").re('.*[0-9]{8}/.*\.htm'):
            url = response.urljoin(url)
            if not self.is_in_scraped_urls(url) and not self.should_stop():
                logger.info("crawling " + url)
                self.add_to_scraped_urls(url)
                yield scrapy.Request(url, callback = self.parse_page)

    def add_to_scraped_urls(self, url):
        #insert url in to scraped_urls
        scraped_urls = self.crawler.stats.get_value("scraped_urls")
        scraped_urls.append(url)
        self.crawler.stats.set_value("scraped_urls", scraped_urls)

    def is_in_scraped_urls(self, url):
        scraped_urls = set(self.crawler.stats.get_value("scraped_urls"))
        return url in scraped_urls

    def should_stop(self):
        return len(self.crawler.stats.get_value("scraped_urls")) >= self.crawler.settings.get("MAX_SCRAPE_URLS", 10000)

    def parse_page(self, response):
        self.issue_new_request(response)
        title = " ".join(response.xpath("//div[@class='hd']/h1/text()").extract())
        if title == "":
            title = " ".join(response.xpath("//div[@id='artical']/h1/text()").extract())
        text = " ".join(response.xpath("//div[@id='Cnt-Main-Article-QQ']//p/text()").extract())
        #text = re.sub(r'[\s,]+', ' ', text) # reduce all continous white spaces.
        if text == "":
            text = " ".join(response.xpath("//div[@id='main_content']/p//text()").extract())
        item = NewsItem()
        item["title"] = title
        item["url"] = response.url
        item["text"] = text
        yield item
