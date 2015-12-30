#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by WildCat. All rights reserved.

import re
import requests
from pyquery import PyQuery

URL_PREFIX = 'http://pub.sdufe.edu.cn'


def request_list_urls(class_id='1102', fetch_all_pages=False):
    """
    Generate a list of urls of a category of news
    :param class_id:
    :param fetch_all_pages:
    :return: [string] URLs

    >>> list_urls = request_list_urls('1102', fetch_all_pages=True)
    >>> len(list_urls) > 1
    True
    """
    urls = ['%s/news/list.php?class_id=%s' % (URL_PREFIX, class_id)]
    if fetch_all_pages is False:
        return urls
    r = requests.get(urls[0])
    r.encoding = 'UTF-8'
    doc = PyQuery(r.text)
    total_page = int(re.search(r'共(\d+)页', doc('#pagelist li:nth-child(5)').text()).group(1))
    next_page_url = doc('#pagelist li:nth-child(2) > a')[0].get('href')
    next_page_url_prefix = re.search(r'^(.+page=)', next_page_url).group(1)
    for page in range(2, total_page + 1):
        urls.append(URL_PREFIX + next_page_url_prefix + str(page))
    return urls


def request_news_list(url):
    """
    Request a news list of SDUFE, and perform the parser.
    :param url: URL of news list
    :return: [news_id]

    >>> news_ids = request_news_list('%s/news/list.php?class_id=1102' % URL_PREFIX)
    >>> len(news_ids)
    15
    """
    r = requests.get(url)
    r.encoding = 'UTF-8'
    doc = PyQuery(r.text)
    elements = doc('.main_new_left ul li a')
    return [re.search(r'id=(\d+)', e.get('href')).group(1) for e in elements]


def request_news(news_id):
    """
    Request a news page
    :param news_id:
    :return: A dictionary of a piece of news

    >>> dict = request_news('31753')
    >>> dict['id'] is not None
    True
    >>> dict['title'] is not None
    True
    >>> dict['category'] is not None
    True
    >>> dict['date'] is not None
    True
    >>> dict['editor'] is not None
    True
    >>> dict['content'] is not None
    True
    """
    r = requests.get('%s/news/view.php?id=%s' % (URL_PREFIX, news_id))
    r.encoding = 'UTF-8'
    doc = PyQuery(r.text)
    meta_string = doc('td[valign="top"] font[color="#666666"]').text()
    editor_element = re.search(r'单位:([^\s]+)', meta_string)
    if editor_element is None:
        editor = ''
    else:
        editor = editor_element.group(1)
    news_dict = {
        'id': news_id,
        'title': doc('div.main_new_view strong').text(),
        'category': doc('div.mian_sub > div > div > div > a:nth-child(2)').text(),
        'date': re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', meta_string).group(0),
        'editor': editor,
        'content': doc('table tr:nth-child(3) td:nth-child(1)').html()
    }
    return news_dict
