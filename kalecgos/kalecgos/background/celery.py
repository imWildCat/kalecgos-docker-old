# -*- coding: utf-8 -*-
# Created by WildCat. All rights reserved.

from __future__ import absolute_import

__author__ = 'wildcat'

import sys
import os

sys.path.append('../')

from celery import Celery

app = Celery('kalecgos', include=['kalecgos.background.tasks'])

app.config_from_object('kalecgos.background.config')

TEMP_PATH = '../temp'
if not os.path.exists(TEMP_PATH):
    os.makedirs(TEMP_PATH)

if __name__ == '__main__':
    app.start()
    # It seems not working
