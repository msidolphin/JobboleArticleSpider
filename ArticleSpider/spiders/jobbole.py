# -*- coding: utf-8 -*-
from scrapy.http import Request
from ArticleSpider.items import ArticlespiderItem
from urllib import parse
from ArticleSpider.utils import security
# scrapy loader
from ArticleSpider.loader.ArticleItemLoader import ArticleItemLoader
import scrapy
import re


# 伯乐在线 文章爬虫
class JobboleSpider(scrapy.Spider):


    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    # root
    start_urls = ['http://blog.jobbole.com/all-posts/']

    # 解析url
    def parse(self, response):
        # response.xpath("//div[@id='archive']//a[@class='archive-title']/@href").extract()
        # 解析列表页面的所有url，交给scrapy自动下载，下载完成后scrapy调用回调函数
        post_nodes = response.css("#archive .post .post-thumb a")
        for post_node in post_nodes:
            main_image_url = post_node.css("img::attr(src)").extract_first("")
            url = parse.urljoin(response.url, post_node.css("::attr(href)").extract_first(""))
            yield Request(url=url, meta={"main_image_url": main_image_url}, callback=self._parse_data)
        # 获取下一页url, 交给scrapy自动下载，但是这是一个列表页面，回调函数应该是parse
        next_page = response.css(".navigation .next::attr(href)").extract()[0]
        if next_page:
            yield Request(url=parse.urljoin(response.url, next_page), callback=self.parse)

    # 解析内容
    def _parse_data(self, response):
        # # 文章item
        # article = ArticlespiderItem()
        # # response对象的body属性就是需要解析的html_doc
        # create_selector = response.xpath('//*[@class="entry-meta-hide-on-mobile"]/text()')
        # # 文章标题
        # title = response.xpath("//div[@class='entry-header']/h1/text()").extract()
        # # 文章创建时间
        # create_date = create_selector.extract()[0].strip().replace("·", "")
        # coll = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract()[0]
        # coll_re = re.compile(r".*?(\d+?).*")
        # coll_match = coll_re.match(coll)
        # # 收藏数
        # stars = 0
        # if coll_match is not None:
        #     stats = int(coll_match.group(1))
        # # 点赞数
        # try :
        #     thumb_ups = int(response.xpath("//span[contains(@class,'vote-post-up')]/h10/text()").extract()[0])
        # except Exception as e:
        #     thumb_ups = 0
        # # 评论数
        # comments = 0
        # comm_re = re.compile(r".*?(\d+?).+")
        # comm_match = comm_re.match(response.xpath("//a[@href='#article-comment']/span/text()").extract()[0])
        # if comm_match is not None:
        #     comments = int(comm_match.group(1))
        # # 正文
        # content = response.xpath("//div[@class='entry']").extract()
        # # tag
        # tag_list = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()
        # tags = ",".join([tag for tag in tag_list if not tag.strip().endswith('评论')])
        #
        # article['title'] = title
        # article['create_date'] = create_date
        # article['url'] = response.url
        # article['url_object_id'] = security.get_md5(response.url)
        # article['main_image_url'] = [response.meta.get("main_image_url", "")]
        # article['content'] = content
        # article['thumb_ups'] = thumb_ups
        # article['comments'] = comments
        # article['stars'] = stars
        # article['tags'] = tags

        # scrapy loader 对比上面...
        loader = ArticleItemLoader(item=ArticlespiderItem(), response=response)
        loader.add_value("url", response.url)
        loader.add_value("url_object_id", security.get_md5(response.url))
        loader.add_value("main_image_url", [response.meta.get("main_image_url", "")])
        loader.add_xpath("title", "//div[@class='entry-header']/h1/text()")
        loader.add_xpath("create_date", '//*[@class="entry-meta-hide-on-mobile"]/text()')
        loader.add_xpath("stars", '//span[contains(@class,"bookmark-btn")]/text()')
        loader.add_xpath("thumb_ups", "//span[contains(@class,'vote-post-up')]/h10/text()")
        loader.add_xpath("comments", "//a[@href='#article-comment']/span/text()")
        loader.add_xpath("content", "//div[@class='entry']")
        loader.add_xpath("tags", "//p[@class='entry-meta-hide-on-mobile']/a/text()")
        # 返回的item需要通过处理函数才能转换成我们想要的类型
        article = loader.load_item()
        # return to pipelines
        yield article