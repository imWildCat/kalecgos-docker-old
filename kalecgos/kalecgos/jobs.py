# -*- coding: utf-8 -*-
# Created by WildCat. All rights reserved.

__author__ = 'wildcat'

import sys

sys.path.append('./')

import time
import logging
import schedule
from kalecgos.background.tasks import perform_latest_news_spider

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def latest_news_spider_job():
    logging.info('[Start] latest_news_spider_job')
    perform_latest_news_spider.delay()

schedule.every().hour.do(latest_news_spider_job)

while True:
    schedule.run_pending()
    time.sleep(1)
