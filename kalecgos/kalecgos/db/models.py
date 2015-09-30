# -*- coding: utf-8 -*-
# Created by WildCat. All rights reserved.

__author__ = 'wildcat'

from sqlalchemy import Column, Integer, String, Text, Enum, DateTime
from kalecgos.db.database import Base


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
