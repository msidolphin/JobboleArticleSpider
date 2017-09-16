# -*- coding: utf-8 -*-
__author__ = "msidolphin"
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst


# 自定义item_loader 作用是统一输出列表的第一个元素
class ArticleItemLoader(ItemLoader):

    default_output_processor=TakeFirst()