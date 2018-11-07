# -*- coding: utf-8 -*-

import scrapy

class DmozItem(scrapy.Item):
    asin = scrapy.Field()
    brand = scrapy.Field()
    url = scrapy.Field()
    keyword = scrapy.Field()
    score= scrapy.Field()
    comment = scrapy.Field()
    bigname = scrapy.Field()
    pass

class gurl(scrapy.Item):
    url = scrapy.Field()
    keyword = scrapy.Field()
    isvalid = scrapy.Field()
    pass

class ukurl(scrapy.Item):
    url = scrapy.Field()
    keyword = scrapy.Field()
    isvalid = scrapy.Field()
    pass

class deurl(scrapy.Item):
    url = scrapy.Field()
    keyword = scrapy.Field()
    isvalid = scrapy.Field()
    pass

class burl(scrapy.Item):
    url = scrapy.Field()
    keyword = scrapy.Field()
    isvalid = scrapy.Field()
    pass