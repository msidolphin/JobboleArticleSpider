# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from datetime import datetime
from twisted.enterprise import adbapi
import codecs
import MySQLdb
import MySQLdb.cursors
import json


class  ArticleSpiderPipeline(object):

    def process_item(self, item, spider):
        return item

'''
    ImagesPipeline源码 
    def get_media_requests(self, item, info):
        return [Request(x) for x in item.get(self.images_urls_field, [])] # 这就是为什么图片url字段需要传递一个数组
    要获取下载图片的path，可以重写item_completed方法，results对象中有图片的下载路径
    def item_completed(self, results, item, info):
        if isinstance(item, dict) or self.images_result_field in item.fields:
            item[self.images_result_field] = [x for ok, x in results if ok]
        return item
'''


class ArticleImagesPipeline(ImagesPipeline):

    # 重写item_completed方法获取下载图片路径
    def item_completed(self, results, item, info):
        # 如果有多个爬虫需要重用此代码，如果不加判断，会导致异常，原因不是所有的item都包含此属性
        if "main_image_url" in item:
            image_path = ""
            for ok, value in results:
                image_path = value['path']
            item['main_image_path'] = image_path
            # remember
            return item
        return item

# 写入json的PipeLine


# 自定义导出json
class ArticleJsonPipeline(object):

    def __init__(self):
        self.file = codecs.open("article.json", "w", encoding="utf-8")

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

    def spider_closed(self):
        self.file.close()

# scrapy exporter 导出json


class ArticleJsonWithExporterPipeline(object):

    def __init__(self):
        self.file = open("article_with_exporter.json", "wb")
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)

    def close_spider(self, spider):
        self.exporter.finish_exporting()


class MysqlPipeline(object):

    def __init__(self):
        # 可以配置到setting中
        self.conn = MySQLdb.connect("127.0.0.1", "root", "root", "jobbole", charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        sql = """
            insert into `article` values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(sql, (item['url_object_id'], item['url'], item['title'], item['create_date'],
                                  item['main_image_url'], item['main_image_path'], str(item['thumb_ups']),
                                  str(item['comments']), str(item['stars']), item['content'], item['tags'])
        )
        self.conn.commit()
        return item



'''
 使用Twisted实现异步的插入操作，上面的方式是同步插入，效率低下，因为存在这么一种情况：爬虫爬取的速度远大于插入速度
'''


class MySQLWithTwistedPipeline(object):

    def __init__(self, db_pool):
        self.db_pool = db_pool

    '''
    此方法由scrapy自动调用，可以用来读取配置文件配置的属性
    settings是Setting对象
    '''
    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings["MYSQL_HOST"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            db=settings["MYSQL_DBNAME"],
            charset="utf8",
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        db_pool = adbapi.ConnectionPool("MySQLdb", **dbparams)
        return cls(db_pool)

    def process_item(self, item, spider):
        query = self.db_pool.runInteraction(self.insert_handler, item)
        # 处理异常
        query.addErrback(self.error_handler)

    def insert_handler(self, cursor, item):
        sql = """
                    insert into `article` values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
        cursor.execute(sql, (
        item['url_object_id'], item['url'], item['title'], item['create_date'], item['main_image_url'][0], item['main_image_path'],
        str(item['thumb_ups']), str(item['comments']), str(item['stars']), item['content'], item['tags']))
        # 无需commit

    def error_handler(self, failure, item, spider):
        print(failure)