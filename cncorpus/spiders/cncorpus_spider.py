import scrapy
import logging
import re
from cncorpus.items import NewsItem

logger = logging.getLogger(__name__)

class NeteaseNewsSpider(scrapy.Spider):
    """
        find all the hyperlinks that match the news url.
        ```
            response.xpath("//a/@href").re('.*[0-9]{2}/[0-9]{4}/[0-9]{2}/.*\.html')
        ```
    """
    name = "netease-news-spider"
    allowed_domains = ["163.com"]
    start_urls = [
        "http://news.163.com/",
        "http://lady.163.com/",
        "http://auto.163.com/",
        "http://sports.163.com/",
        "http://sports.163.com/nba/",
        "http://ent.163.com/",
        "http://money.163.com/",
        "http://money.163.com/stock/",
        "http://tech.163.com/",
        "http://digi.163.com/",
        "http://travel.163.com/",
        "http://house.163.com/",
        "http://home.163.com/",
        "http://play.163.com/",
        "http://jiankang.163.com/",
        "http://jiu.163.com/",
        "http://edu.163.com/"
    ]
    #crawed_urls = set(start_urls)

    def parse(self, response):
        return self.issue_new_request(response)

    def issue_new_request(self, response):
        for url in response.xpath("//a/@href").re('.*[0-9]{2}/[0-9]{4}/[0-9]{2}/.*\.html'):
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
        return len(self.crawler.stats.get_value("scraped_urls")) >= 15

    def parse_page(self, response):
        self.issue_new_request(response)
        title = " ".join(response.css("#h1title").xpath("text()").extract())
        title = re.sub(r'[\s,]+', ' ', title)
        text = " ".join(response.css("#endText").xpath("p/text()").extract())
        text = re.sub(r'[\s,]+', ' ', text) # reduce all continous white spaces.
        item = NewsItem()
        item["title"] = title
        item["url"] = response.url
        item["text"] = text
        yield item
