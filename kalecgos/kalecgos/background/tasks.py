# -*- coding: utf-8 -*-
# Created by WildCat. All rights reserved.

from __future__ import absolute_import

__author__ = 'wildcat'

import sys

sys.path.append('../../')
sys.path.append('../')

from kalecgos.background.celery import app

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from kalecgos.spiders.latest_news import LatestNewsSpider
from kalecgos.spiders.news import NewsSpider

@app.task
def add():
    print("hi")


settings = Settings()

# crawl settings
settings.set("USER_AGENT",
             "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36")
settings.set("ITEM_PIPELINES", {
    'kalecgos.pipelines.KalecgosPipeline': 300,
})

@app.task
def perform_latest_news_spider():
    process = CrawlerProcess(settings)
    process.crawl(LatestNewsSpider)
    process.start()

@app.task
def perform_news_spider():
    process = CrawlerProcess(settings)
    process.crawl(NewsSpider)
    process.start()
