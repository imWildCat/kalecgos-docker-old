# -*- coding: utf-8 -*-
# Created by WildCat. All rights reserved.

__author__ = 'wildcat'

import re
from dateutil import parser
from datetime import datetime
import requests
from pyquery import PyQuery as pq

s = requests.Session()

r = s.post('http://filex.sdufe.edu.cn/down.php', data={'code': '123', 'Submit': '1', 'vcode': '1'})

selector = pq(r.content.decode('gbk'))

download_link_elements = selector('a')

files = [{'name': e.text, 'url': e.attrib['href']} for e in download_link_elements]

# Handle time
date_string_raw = selector('table font[size="2"]').text()
date_string = re.search(ur'过期时间:(.+)', date_string_raw).group(1)
dt = parser.parse(date_string)
timestamp = int((dt - datetime(1970, 1, 1)).total_seconds()) - 28800

print(len(download_link_elements))
print(files)
print(date_string_raw)
print(timestamp)


def download_file(session, name, url):
    local_filename = './temp/' + name
    # NOTE the stream=True parameter
    # The system of school requires referer
    r = session.get(url, stream=True, headers={'referer': 'http://filex.sdufe.edu.cn/down.php'})
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()


for f in files:
    download_file(s, f['name'], 'http://filex.sdufe.edu.cn/' + f['url'])
