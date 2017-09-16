# -*- coding: utf-8 -*-
__author__ = "msidolphin"

from scrapy.cmdline import execute
import sys
import os

'''
sys.path.append("...") : 当我们导入某个模块时，当我们导入一个模块时：
import  xxx，默认情况下python解析器会搜索当前目录、已安装的内置模块和第三方模块，搜索路径存放在sys模块的path中
该路径已经添加到系统的环境变量了，当我们要添加自己的搜索目录时，可以通过列表的append()方法
可以将该路径写死，可以一旦目录改变了，就会出问题

'''
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# print(os.path.dirname(os.path.abspath(__file__))) # 获取main.py目录的绝对路径  F:\pySpider\ArticleSpider
execute(["scrapy", "crawl", "jobbole"]) # 配置scrapy 命令 相当于在命令行中使用scrapy crawl jobbole 命令启动一个爬虫
# 这样就在pycharm中调试scrapy了
