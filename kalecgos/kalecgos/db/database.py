# -*- coding: utf-8 -*-
# Created by WildCat. All rights reserved.

__author__ = 'wildcat'

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

env = os.getenv('ENV', 'development')

if env == 'production':
    engine = create_engine('mysql://root:passwd@db:3306/sdufe?charset=utf8', convert_unicode=True, pool_size=20,
                           max_overflow=0)
else:
    engine = create_engine('mysql://root@127.0.0.1/sdufe?charset=utf8', convert_unicode=True, pool_size=20,
                           max_overflow=0, echo=True)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()

    Base.metadata.create_all(bind=engine)
