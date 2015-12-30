#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by WildCat. All rights reserved.

import os
import qiniu

qiniu_access_key = os.getenv('QINIU_AK', '')
qiniu_secret_key = os.getenv('QINIU_SK', '')
qiniu_bucket_name = os.getenv('QINIU_BN', '')
qiniu_bucket_domain = os.getenv('QINIU_DOMAIN', '')

qiniu_auth = qiniu.Auth(qiniu_access_key, qiniu_secret_key)
