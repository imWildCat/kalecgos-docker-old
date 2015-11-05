# -*- coding: utf-8 -*-
# Created by WildCat. All rights reserved.

__author__ = 'wildcat'

import re
from dateutil import parser
from datetime import datetime
import requests
from pyquery import PyQuery as pq

from kalecgos.db.database import db_session
from kalecgos.db.models import File, FileCode

from kalecgos.background.tasks import perform_download


def filex_handler(file_code):
    """

    :param file_code: Downloading code for files in the side of SDUFE
    """
    s = requests.Session()

    r = s.post('http://filex.sdufe.edu.cn/down.php', data={'code': file_code, 'Submit': '1', 'vcode': '1'})

    selector = pq(r.content.decode('gbk'))

    download_link_elements = selector('a')

    files = [{'name': e.text, 'url': e.attrib['href']} for e in download_link_elements]
    file_names = [e.text for e in download_link_elements]

    if len(files) < 1:
        return None, file_names, False

    # Handle time
    date_string_raw = selector('table font[size="2"]').text()
    date_string = re.search(ur'过期时间:(.+)', date_string_raw).group(1)
    dt = parser.parse(date_string)
    timestamp = int((dt - datetime(1970, 1, 1)).total_seconds()) - 28800

    # Check if current code is exist
    file_code_record = FileCode.query.filter(FileCode.code == file_code).filter(
        FileCode.expires_at == timestamp).first()
    if file_code_record is None or file_code_record.status == 0:
        if file_code_record is None:
            description = ''
            for name in file_names:
                description += name + ', '
            description = description[:-2]
            file_code_record = FileCode(code=file_code, expires_at=timestamp, description=description)
            db_session.add(file_code_record)
            db_session.commit()
        perform_download.delay(files, file_code_record.id, s, timestamp, file_code)
        return file_code_record, file_names, False
    return file_code_record, file_names, True

    # print(len(download_link_elements))
    # print(files)
    # print(date_string_raw)
    # print(timestamp)
