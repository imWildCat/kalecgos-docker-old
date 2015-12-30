# -*- coding: utf-8 -*-
# Created by WildCat. All rights reserved.


import sys
import os

sys.path.append('./')

import time
from flask import Flask, session, redirect, url_for, escape, request, jsonify, g
from flask_json import FlaskJSON, JsonError, json_response, as_json
from kalecgos.db.models import News, Device, FileCode, devices_and_file_codes_table
from kalecgos.db.database import init_db, db_session
from downloader import filex_handler

API_V1_PREFIX = '/api/v1/'

app = Flask(__name__)

app.config['JSON_ADD_STATUS'] = True
app.config['JSON_STATUS_FIELD_NAME'] = 'status'
app.config['JSON_DATETIME_FORMAT'] = 'YYYY-MM-DDTHH:MM:SS.mmmmmm'


@app.before_request
def before_request():
    g.request_start_time = time.time()
    g.request_time = lambda: "%.5fms" % ((time.time() - g.request_start_time) * 1000)


@app.after_request
def after_request(response):
    print('Rendered in %s' % g.request_time())
    token = request.headers.get('token')
    print('Token: %s' % token)
    return response

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
    print("test")


@app.route('/')
def index():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    return jsonify({'a': 2})


@app.route(API_V1_PREFIX + 'status')
def status():
    return json_response(server_status=True, latest_client_version='0.1.0')


@app.route(API_V1_PREFIX + 'news/category/<int:category_id>/page/<int:page>')
def news_list(category_id, page):
    if category_id < 1:
        category_id = 1

    if page < 1:
        page = 1

    per_page = 20
    offset = per_page * (page - 1)

    category_name = News.category_id_to_value(category_id)

    ret = News.query.with_entities(News.id, News.title, News.date, News.editor).filter(News.category == category_name). \
        order_by(News.id.desc()).limit(per_page).offset(offset).all()

    count = len(ret)
    has_new_page = False
    if count > 0:
        has_new_page = True

    ret = [{News.id.name: r[0], News.title.name: r[1], News.date.name: r[2].isoformat(), News.editor.name: r[3]} for r
           in ret]

    return json_response(news_list=ret, page=page, category_id=category_id, category_name=category_name, count=count,
                         has_more_page=has_new_page)


@app.route(API_V1_PREFIX + 'news/id/<int:news_id>')
def single_news(news_id):
    news = News.query.get(news_id)
    if news is None:
        return json_response(error_code=404, error_message='新闻未找到。')
    else:
        return json_response(id=news.id, title=news.title, category=news.category, date=news.date.isoformat(),
                             editor=news.editor,
                             content=news.content)


@app.route(API_V1_PREFIX + 'token/gen/<int:device_type_id>')
def gen_device_token(device_type_id):
    device = Device()
    device.type = Device.device_type_id_to_type(device_type_id)
    db_session.add(device)
    db_session.commit()
    return json_response(uid=device.uid)


@app.route(API_V1_PREFIX + 'device/check')
def check_device_token():
    token = request.headers.get('token')

    if token is not None:
        device = Device.query.filter_by(uid=token).first()
        if device is not None:
            return json_response(is_valid=True)
    return json_response(error_code=403, error_message='设备 token 无效。')


@app.route(API_V1_PREFIX + 'file_code/add/<string:file_code>')
def download_file(file_code):
    token = request.headers.get('token')

    if token is not None:
        device = Device.query.filter_by(uid=token).first()
        if device is not None:
            file_code_record, description, is_downloaded = filex_handler(file_code)
            if file_code_record is None:
                return json_response(error_code=400, error_message='不存在此提取码。')
            else:
                device.file_codes.append(file_code_record)
                db_session.add(device)
                db_session.commit()

                return json_response(
                    file_code_id=file_code_record.id,
                    description=description,
                    is_downloaded=is_downloaded,
                    file_code=file_code
                )
    return json_response(error_code=403, error_message='您尚未登录。')


@app.route(API_V1_PREFIX + 'file_code/list')
def filex_list():
    token = request.headers.get('token')
    if token is not None:
        device = Device.query.filter_by(uid=token).first()
        file_codes = [{'id': fc.id, 'description': fc.description, 'is_downloaded': fc.status == 1,
                       'created_at': fc.created_at.isoformat(), 'code': fc.code} for fc in list(reversed(device.file_codes))]
        if device is not None:
            return json_response(
                file_codes=file_codes,
            )
    return json_response(error_code=403, error_message='您尚未登录。')


@app.route(API_V1_PREFIX + 'file_code/<int:file_code_id>')
def filex_get(file_code_id):
    token = request.headers.get('token')
    if token is not None:
        device = Device.query.filter_by(uid=token).first()
        if device is not None:
            dfc = db_session.query(devices_and_file_codes_table).filter_by(device_id=device.id,
                                                                           file_code_id=file_code_id).first()
            print(dfc)
            if dfc is not None:
                file_code = FileCode.query.get(file_code_id)
                files = [{'name': f.name, 'url': f.gen_url()} for f in file_code.files]
                return json_response(files=files, code=file_code.code, created_at=file_code.created_at.isoformat())
            else:
                return json_response(error_code=403, error_message='您无此文件。')
    return json_response(error_code=403, error_message='您尚未登录。')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
    '''


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))


# set the secret key.  keep this really secret:
# app.secret_key = 'xxx'

if __name__ == '__main__':
    env = os.getenv('ENV', 'development')
    if env == 'development':
        app.debug = True
        print('App start in development mode.')
    else:
        app.debug = True
        print('App start in production mode.')
    app.run(host='0.0.0.0')
