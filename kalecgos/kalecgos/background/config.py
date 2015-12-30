# -*- coding: utf-8 -*-
# Created by WildCat. All rights reserved.

from __future__ import absolute_import

import os
from datetime import timedelta

env = os.getenv('ENV', 'development')
if env == 'development':
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/2'
    BROKER_URL = 'redis://localhost/3'
else:
    CELERY_RESULT_BACKEND = 'redis://redis/2'
    BROKER_URL = 'redis://redis/3'

CELERYBEAT_SCHEDULE = {
    'add-every-30-seconds': {
        'task': 'kalecgos.background.tasks.perform_latest_news_spider',
        'schedule': timedelta(hours=1),
        # 'args': (16, 16)
    },
}

CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']

CELERY_TIMEZONE = 'Asia/Shanghai'
