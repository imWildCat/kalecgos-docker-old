# -*- coding: utf-8 -*-
# Created by WildCat. All rights reserved.

from __future__ import absolute_import

__author__ = 'wildcat'

import sys

sys.path.append('../')
sys.path.append('./')

from celery import Celery

app = Celery('kalecgos', include=['kalecgos.background.tasks'])

app.config_from_object('kalecgos.background.config')

if __name__ == '__main__':
    app.start()
