# -*- coding: utf-8 -*-
# Created by WildCat. All rights reserved.

from __future__ import absolute_import

__author__ = 'wildcat'

import sys

sys.path.append('../../')
sys.path.append('../')

import os
import qiniu
import hashlib

from kalecgos.background.celery import app

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from kalecgos.spiders.latest_news import LatestNewsSpider
from kalecgos.spiders.news import NewsSpider

from db.database import db_session
from db.models import File, FileCode

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

TEMP_PATH = '../temp'

if not os.path.exists(TEMP_PATH):
    os.makedirs(TEMP_PATH)

qiniu_access_key = os.getenv('QINIU_AK', '')
qiniu_secret_key = os.getenv('QINIU_SK', '')
qiniu_bucket_name = os.getenv('QINIU_BN', '')
qiniu_bucket_domain = os.getenv('QINIU_DOMAIN', '')

q = qiniu.Auth(qiniu_access_key, qiniu_secret_key)


@app.task
def perform_download(files, file_code_record_id, session, timestamp, file_code):
    for file_info in files:
        download_file(code_id=file_code_record_id, session=session, name=file_info['name'],
                      url='http://filex.sdufe.edu.cn/' + file_info['url'],
                      timestamp=timestamp, file_code=file_code)
    file_code_record = FileCode.query.get(file_code_record_id)
    count = db_session.query(File).with_parent(file_code_record, "files").count()
    if count == len(files):
        file_code_record.status = 1
        db_session.bulk_save_objects([file_code_record], update_changed_only=True)
        db_session.commit()
        return file_code_record.id
    return None


def download_file(code_id, session, name, url, timestamp, file_code):
    local_filename = 'TEMP_PATH/' + name

    # Generate hash and remote file name
    m = hashlib.md5()
    m.update(name.encode('utf-8'))
    file_name_hash = m.hexdigest()
    extension = os.path.splitext(name)[1]
    remote_file_name = u'%s_%s_%s%s' % (file_code, timestamp, file_name_hash, extension)

    file = db_session.query(File).filter(File.remote_name == remote_file_name).first()

    if file is None:
        # NOTE the stream=True parameter
        # The system of school requires referer
        file_response = session.get(url, stream=True, headers={'referer': 'http://filex.sdufe.edu.cn/down.php'})
        with open(local_filename, 'wb') as f:
            for chunk in file_response.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return upload_file(code_id=code_id, file_name=name, remote_file_name=remote_file_name)
    else:
        return file.id


def upload_file(code_id, file_name, remote_file_name):
    # Upload the file
    data = open('TEMP_PATH/' + file_name)
    token = q.upload_token(qiniu_bucket_name)
    ret, info = qiniu.put_data(token, remote_file_name, data)

    # Remove local file
    os.remove('TEMP_PATH/' + file_name)

    if ret is not None:
        print('%s is uploaded.' % file_name)
        f = File(code_id=code_id, name=file_name, remote_name=remote_file_name)
        db_session.add(f)
        db_session.commit()

        # Generate URL:
        # base_url = u'http://%s/%s' % (qiniu_bucket_domain, remote_file_name)
        # private_url = q.private_download_url(base_url.encode('utf-8'), expires=900)  # Expires in 15 minutes
        # print(private_url)
        return f.id
    else:
        print(info.encode('utf-8'))
        return None
