from celery import task
from .models import News
from .spiders.school_news import request_list_urls, request_news_list, request_news
from django.utils.dateparse import parse_datetime
from django.utils.timezone import get_current_timezone

SDUFE_NEWS_CLASS_IDS = [
    '1002',
    '1115',
    '1102',
    '1116',
    '1109',
    '1105',
    '1108',
    '1102',
    '1113',
    '1103',
    '1111',
    '1104',
    '1110',
]


@task
def test():
    print(News.objects.all())
    print('The test task executed with argument')


@task
def perform_crawl_latest_news():
    _perform_news_tasks(False)


def _perform_news_tasks(fetch_all_pages):
    for class_id in SDUFE_NEWS_CLASS_IDS:
        crawl_news_category_urls.delay(class_id, fetch_all_pages=fetch_all_pages)


@task
def crawl_news_category_urls(class_id, fetch_all_pages):
    list_urls = request_list_urls(class_id, fetch_all_pages=fetch_all_pages)
    for url in list_urls:
        crawl_news_urls.delay(url)


@task
def crawl_news_urls(url):
    news_ids = request_news_list(url)
    for news_id in news_ids:
        crawl_single_news.delay(news_id)


@task
def crawl_single_news(news_id):
    news_dict = request_news(news_id)
    news = News(
            id=int(news_dict['id']),
            title=news_dict['title'],
            category=news_dict['category'],
            date=get_current_timezone().localize(parse_datetime(news_dict['date'])),
            editor=news_dict['editor'],
            content=news_dict['content']
    )
    news.save()
