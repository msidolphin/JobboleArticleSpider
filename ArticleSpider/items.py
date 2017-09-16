# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.loader.processors import MapCompose, TakeFirst, Join
from datetime import datetime
import scrapy
import re


# 日期转换
def date_convertor(value):
    try:
        return datetime.strptime(value, "%Y/%m/%d")
    except Exception as e:
        return datetime.now().date()


def integer_handler(value):
    regex = re.compile(r".*?(\d+).*")
    res = regex.match(value)
    if res is not None:
        return int(res.group(1))
    else:
        return 0


# 判断value是否是以评论结尾的字符串
def is_comment(value):
    if "评论" in value:
        return None
    return value


def do_not_thing(value):
    return value


# 解析dom后，将参数封装在ITEM中，yield ITEM 将Item传递给pipelines
class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    '''
    create table article(
     url_object_id varchar(128) primary key,
     url varchar(300) not null,
     title varchar(300) not null,
     create_date date not null,
     main_image_url varchar(300),
     main_image_path varchar(200),
     thumb_ups int default 0,
     comments int default 0,
     stars int default 0,
     content longtext,
     tags varchar(200)
     )engine=innodb,charset=utf8;
    '''

    # 文章标题
    title = scrapy.Field()
    # 创建时间
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convertor)
        # output_processor=TakeFirst()
    )
    # 文章url
    url = scrapy.Field()
    # url_object_id
    url_object_id = scrapy.Field()
    # 文章主图
    main_image_url = scrapy.Field(
        output_processor=MapCompose(do_not_thing)
    )
    # 文章主图保存路径
    main_image_path = scrapy.Field()
    # 文章内容
    content = scrapy.Field()
    # 点赞数
    thumb_ups = scrapy.Field(
        input_processor=MapCompose(integer_handler)
    )
    # 评论数
    comments = scrapy.Field(
        input_processor=MapCompose(integer_handler)
    )
    # 收藏数
    stars = scrapy.Field(
        input_processor=MapCompose(integer_handler)
    )
    # 标签
    tags = scrapy.Field(
        input_processor=MapCompose(is_comment),
        output_processor=Join(",")
    )
