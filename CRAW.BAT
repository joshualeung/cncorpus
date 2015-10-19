REM scrapy crawl netease-news-spider -o data/net-ease-news.csv
REM scrapy crawl netease -o data/netease.csv
scrapy crawl ifeng -o data/ifeng.csv > data/infeng.log
scrapy crawl tencent -o data/tencent.csv > data/tencent.log
pause
