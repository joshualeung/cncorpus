# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import jieba

class NewsPipeline(object):
    def process_item(self, item, spider):
        if item["text"] and len(item["text"].strip()) > 0:
            tokens = jieba.lcut(item["text"], cut_all = False)
            self.file.write(" ".join(tokens).encode("utf8"))
        return item

    def open_spider(self, spider):
        save_path = spider.crawler.settings.get("CORPUS_SAVE_PATH", "data/default.txt")
        self.file = open(save_path, "w")
    #def close_spider(self, spider)
