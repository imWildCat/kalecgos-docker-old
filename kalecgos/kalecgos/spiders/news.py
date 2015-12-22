# -*- coding: utf-8 -*-
# Created by WildCat. All rights reserved.

__author__ = 'wildcat'

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector

from pyquery import PyQuery as pq

from kalecgos.items import NewsItem
import re


class NewsSpider(CrawlSpider):
    name = "news"
    allowed_domains = ["pub.sdufe.edu.cn"]

    start_urls = (
        'http://pub.sdufe.edu.cn/news/list.php',
    )

    rules = [
        Rule(LinkExtractor(allow='list\.php\?filter=&page=\d+$')),
        Rule(LinkExtractor(allow='view\.php\?id=\d+$'), callback='parse_news'),
    ]

    # def parse(self, response):
    #     sel = Selector(response)
    #     news_list = sel.css('ul.neirong1_lista li a')
    #     print(news_list[0].extract())

    def parse_news(self, response):
        sel = Selector(response)
        id = 0

        s = re.search(r'id=(\d+)', response.url)
        if s:
            id = s.group(1)

        item = NewsItem()
        item['id'] = id
        item['title'] = sel.css('div.main_new_view strong::text')[0].extract()
        item['category'] = sel.css('body > div.mian_sub > div > div > div > a:nth-child(2)::text')[0].extract()
        meta_string = sel.xpath('//td[@valign="top"]//font[@color="#666666"]/text()')[0].extract()
        date_string = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', meta_string).group(0)
        editor_element = re.search(ur'单位:([\u4E00-\u9FA5]+)', meta_string)
        if editor_element is None:
            editor_string = ''
        else:
            editor_string = re.search(ur'单位:([\u4E00-\u9FA5]+)', meta_string).group(1)
        item['date'] = date_string
        item['editor'] = editor_string
        d = pq(response.body)
        item['content'] = d('table tr:nth-child(3) td:nth-child(1)').html()

        if id > 0:
            return item
