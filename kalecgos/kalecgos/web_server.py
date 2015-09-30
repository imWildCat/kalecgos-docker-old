# -*- coding: utf-8 -*-
# Created by WildCat. All rights reserved.

__author__ = 'wildcat'

import sys
import os

sys.path.append('./')

import time
from flask import Flask, session, redirect, url_for, escape, request, jsonify, g
from flask_json import FlaskJSON, JsonError, json_response, as_json
from json import dumps
from kalecgos.db.models import *
from kalecgos.db.database import init_db

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
    return response


@app.route('/')
def index():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    return jsonify({'a': 2})

@app.route('/api/v1/status')
def status():
    return json_response(server_status=True, latest_client_version='0.1.0')

@app.route('/api/v1/news/category/<int:category_id>/page/<int:page>')
def news_list(category_id, page):
    if category_id < 1:
        category_id = 1

    if page < 1:
        page = 1

    per_page = 20
    offset = per_page * (page - 1)

    ret = News.query.with_entities(News.id, News.title, News.date, News.editor).filter(News.category == News.category_id_to_value(category_id)). \
        order_by(News.id.desc()).limit(per_page).offset(offset).all()

    ret = [{News.id.name: r[0], News.title.name: r[1], News.date.name: r[2].isoformat(), News.editor.name: r[3]} for r in ret]

    return json_response(news_list=ret)


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
    init_db()
    app.run(host='0.0.0.0')
