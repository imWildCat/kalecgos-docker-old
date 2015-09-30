# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from kalecgos.db.database import init_db, db_session
from kalecgos.db.models import *
from kalecgos.items import *


class KalecgosPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, NewsItem):
            self.process_news(item)
        return item

    def process_news(self, item):
        try:
            print('Category is ' + item['category'])
            n = News(id=item['id'], title=item['title'], category=item['category'], date=item['date'],
                     editor=item['editor'], content=item['content'])
            db_session.bulk_save_objects([n], update_changed_only=False)
            db_session.commit()
        except Exception, e:
            print("wrong item: %s" % e)
        finally:
            pass

    def open_spider(self, spider):
        init_db()

    def close_spider(self, spider):
        db_session.remove()
