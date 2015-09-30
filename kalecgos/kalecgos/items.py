# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class KalecgosItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class NewsItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    category = scrapy.Field()
    editor = scrapy.Field()
    date = scrapy.Field()
    content = scrapy.Field()

