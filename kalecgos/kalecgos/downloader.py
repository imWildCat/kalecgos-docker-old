# -*- coding: utf-8 -*-
# Created by WildCat. All rights reserved.

__author__ = 'wildcat'

import re
import sys
import os
import hashlib
from dateutil import parser
from datetime import datetime
import requests
from pyquery import PyQuery as pq
import qiniu

sys.path.append('../')

from db.database import db_session
from db.models import File, FileCode

qiniu_access_key = os.getenv('QINIU_AK', '')
qiniu_secret_key = os.getenv('QINIU_SK', '')
qiniu_bucket_name = os.getenv('QINIU_BN', '')
qiniu_bucket_domain = os.getenv('QINIU_DOMAIN', '')

q = qiniu.Auth(qiniu_access_key, qiniu_secret_key)


def download_file(code_id, session, name, url, timestamp, file_code):
    local_filename = './temp/' + name

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
    data = open('./temp/' + file_name)
    token = q.upload_token(qiniu_bucket_name)
    ret, info = qiniu.put_data(token, remote_file_name, data)

    # Remove local file
    os.remove('./temp/' + file_name)

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


def filex_handler(file_code):
    """

    :param file_code: Downloading code for files in the side of SDUFE
    """
    s = requests.Session()

    r = s.post('http://filex.sdufe.edu.cn/down.php', data={'code': file_code, 'Submit': '1', 'vcode': '1'})

    selector = pq(r.content.decode('gbk'))

    download_link_elements = selector('a')

    files = [{'name': e.text, 'url': e.attrib['href']} for e in download_link_elements]

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
            file_code_record = FileCode(code=file_code, expires_at=timestamp)
            db_session.add(file_code_record)
            db_session.commit()
        for file_info in files:
            download_file(code_id=file_code_record.id, session=s, name=file_info['name'],
                          url='http://filex.sdufe.edu.cn/' + file_info['url'],
                          timestamp=timestamp, file_code=file_code)
        count = db_session.query(File).with_parent(file_code_record, "files").count()
        if count == len(files):
            file_code_record.status = 1
            db_session.bulk_save_objects([file_code_record], update_changed_only=True)
            db_session.commit()
            return file_code_record.id
        return None
    else:
        return file_code_record.id

        # print(len(download_link_elements))
        # print(files)
        # print(date_string_raw)
        # print(timestamp)


code = u'111'

filex_handler(code)
