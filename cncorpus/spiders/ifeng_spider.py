# -*- coding: utf-8 -*-
import re
import scrapy
import logging
from cncorpus.items import NewsItem

logger = logging.getLogger(__name__)

class IFengNewsSpider(scrapy.Spider):
    """
        凤凰网(www.ifeng.com)新闻语料爬取
    """
    name = "ifeng"
    allowed_domains = ["ifeng.com"]
    start_urls = [
        "http://www.ifeng.com/"
    ]
    custom_settings = {
        "CORPUS_SAVE_PATH": "data/ifeng.txt",
        "MAX_SCRAPE_URLS": 100000
    }

    def parse(self, response):
        nav_urls = response.xpath("//div[@class='NavM']//li//a/@href").extract()
        nav_urls.extend(response.xpath("//div[@class='NavM']//li//a/@href").extract())
        page_urls = response.xpath("//a/@href").re('.*[0-9]{8}/.*\.shtml')
        page_urls.extend(response.xpath("//a/@href").re('.*detail_[0-9]{4}_[0-9]{2}/[0-9]{2}.*\.shtml'))
        page_urls.extend(nav_urls)
        for url in set(page_urls):
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
        self.parse(response)
        title = " ".join(response.xpath("//div[@class='arl-cont']/h3/text()").extract())
        if title == "":
            title = " ".join(response.xpath("//div[@id='artical']/h1/text()").extract())
        text = " ".join(response.xpath("//div[@class='arl-c-txt']/p//text()").extract())
        if text == "":
            text = " ".join(response.xpath("//div[@id='main_content']/p//text()").extract())
        item = NewsItem()
        item["title"] = title
        item["url"] = response.url
        item["text"] = text
        yield item
