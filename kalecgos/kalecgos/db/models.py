# -*- coding: utf-8 -*-
# Created by WildCat. All rights reserved.

from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey, Index, CHAR, Table
from sqlalchemy.orm import relationship, backref
from kalecgos.db.database import Base
from kalecgos.utils.qiniu_util import qiniu_auth, qiniu_bucket_domain

import base64
import uuid
import datetime


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    email = Column(String(121), unique=True, nullable=False)

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return '%s (%r, %r)' % (self.__class__.__name__, self.name, self.email)


devices_and_file_codes_table = Table('devices_and_file_codes', Base.metadata,
                                     Column('device_id', Integer, ForeignKey('devices.id')),
                                     Column('file_code_id', Integer, ForeignKey('file_codes.id'))
                                     )


def gen_uid():
    uid = uuid.uuid4().bytes
    r_uuid = base64.urlsafe_b64encode(uid)
    return r_uuid.replace('=', '')


class Device(Base):
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True)
    uid = Column(CHAR(22), primary_key=True, unique=True)
    type = Column(Enum(u'ios', u'android'), nullable=False)
    created_at = Column(DateTime, nullable=False)
    file_codes = relationship('FileCode', secondary=devices_and_file_codes_table)

    def __init__(self):
        self.created_at = datetime.datetime.now()
        self.uid = gen_uid()

    def __repr__(self):
        return '%s [%s](%s)' % (self.__class__.__name__, self.uid, self.id)

    @staticmethod
    def device_type_id_to_type(device_type_id):
        return ['ios', 'android'][device_type_id - 1]


class News(Base):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True)
    title = Column(String(127), nullable=False)
    category = Column(
        Enum(u'综合新闻', u'新闻头条', u'新闻聚焦', u'院系动态', u'媒体财大', u'讲座报告', u'通知公告', u'讲座预告',
             u'校园传真', u'影像财大', u'领导讲话', u'财大论坛', u'人物风采', u'视频财大'), nullable=False)
    date = Column(DateTime(), nullable=False)
    editor = Column(String(127), nullable=False)
    content = Column(Text, nullable=False)

    def __init__(self, id=None, title=None, category=None, date=None, editor=None, content=None):
        self.id = id
        self.title = title
        self.category = category
        self.date = date
        self.editor = editor
        self.content = content

    def __repr__(self):
        return '%s (%r, %r)' % (self.__class__.__name__, self.id, self.title)

    @staticmethod
    def category_id_to_value(category_id):
        category_names = (u'综合新闻', u'新闻头条', u'新闻聚焦', u'院系动态', u'媒体财大', u'讲座报告', u'通知公告', u'讲座预告',
                          u'校园传真', u'影像财大', u'领导讲话', u'财大论坛', u'人物风采', u'视频财大')

        return category_names[category_id - 1]


class FileCode(Base):
    __tablename__ = 'file_codes'

    id = Column(Integer, primary_key=True)
    code = Column(String(127), nullable=False)
    created_at = Column(DateTime, nullable=False)
    expires_at = Column(Integer, nullable=False)
    status = Column(Integer, nullable=False, default=0)
    description = Column(String(127), nullable=True)
    files = relationship('File', backref='code')

    Index('code_expires_at_unique', code, expires_at, unique=True)

    def __init__(self, code=None, expires_at=None, description=None):
        self.code = code
        self.created_at = datetime.datetime.now()
        self.expires_at = expires_at
        self.description = description


class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    code_id = Column(Integer, ForeignKey('file_codes.id'))
    name = Column(String(255), nullable=False)
    remote_name = Column(String(255), nullable=False, unique=True)

    Index('code_id_remote_name_unique', remote_name, unique=True)

    def __init__(self, code_id, name, remote_name):
        self.code_id = code_id
        self.name = name
        self.remote_name = remote_name

    def gen_url(self):
        # Generate URL:
        base_url = u'http://%s/%s' % (qiniu_bucket_domain, self.remote_name)
        return qiniu_auth.private_download_url(base_url.encode('utf-8'), expires=900)  # Expires in 15 minutes