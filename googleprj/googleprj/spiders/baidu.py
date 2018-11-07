# -*- coding: utf-8 -*-
import scrapy
from googleprj.items import DmozItem,gurl
from lxml import etree
import re
import urllib
import requests
from googleprj.settings import *
from _mysql import NULL
from googleprj.redisM import RedisM
import time
import MySQLdb

keywords = None
db = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB)
cursor = db.cursor()
real_key = ""
rm = RedisM()

class baidu(scrapy.Spider):
    name = "baiduprj"
    allowed_domains = ["baidu.com","amazon.com"]
    
    def start_requests(self):
        global keywords,real_key
        
        #填充IP池
        if rm.getvalue("baidupool") == None or len(rm.getvalue("baidupool"))<5:
            rm.pushredis("baidupool",IPPOOL)
        
        sql = "select keyword from tb_keywords where isvalid=1"
        try:
            cursor.execute(sql)
            keywords = cursor.fetchall()
        except Exception,e:
            print e
        
        for key in keywords:
            key = key[0]
            real_key = key
            #check if exist last url
            last = rm.checkExist(key+"baidu")
            #last = None
            if last == None:
                print 'first start 11111111'
                url = 'https://www.baidu.com/s?wd=site%3Aamazon.com+'+key.replace(" ", "+").replace("&","%26")+'+currently+unavailable&tn=87048150_dg&ie=utf8'
                yield scrapy.Request(url=url, callback=self.parse,meta={'cookiejar':1,"keyword":key},headers=BAIDU_HEADERS)
            else :
                url = last
                print 'second start 222222222'
                print key
                print url
                yield scrapy.Request(url=url, callback=self.parse,meta={'cookiejar':1,"keyword":key},headers=BAIDU_HEADERS)
            rm.close(real_key)
            
    def parse(self, response):
        global real_key
        try:
            
            list = response.xpath('//div[@id="content_left"]/div/h3')  
            change_proxy = False
            if list == None or len(list)<0:
                change_proxy = True
                
            for one in list:
                baidu_url = requests.get(url=one.xpath("a/@href")[0].extract(), allow_redirects=False)  
                real_url = baidu_url.headers['Location']  #得到网页原始地址  '
                
                if "https://www.amazon.com" in real_url or "http://amazon.com" in real_url:
                    keytemp = response.request.url
                    keytemp = keytemp[keytemp.find('amazon.com')+10:keytemp.find('currently')].replace("%20"," ").replace("%27","").replace("%26","&").replace("+"," ").replace("'","")
                    keytemp = keytemp.strip()
                    real_url = real_url.replace("http://www.amazon.com","https://www.amazon.com")
                    item = gurl()
                    item['url'] =  real_url
                    item['keyword'] = keytemp
                    item['isvalid'] = 1
                    yield item
                    
            forbbiden = response.xpath('//*[@id="content"]/text()')
            if len(forbbiden)>0 and u'验证码' in forbbiden[0].extract():
                change_proxy = True
                print forbbiden[0].extract()
                yield scrapy.Request(url=nexturl, callback=self.parse, meta={'cookiejar':response.meta['cookiejar'],'change_proxy':change_proxy,"keyword":response.request.meta["keyword"],'proxy':response.request.meta["proxy"]},headers=BAIDU_HEADERS)
            else:
                #查找是否有下一页
                nexturl = "https://www.baidu.com"
                nextpages = response.xpath('//div[@id="page"]/a') 
        
                for one in nextpages:
                    if len(one.xpath("text()"))>0:
                        if(u"下一页" in one.xpath("text()")[0].extract()):
                            nexturl += one.xpath("@href")[0].extract()
                print "nexturl:"+nexturl
                if nexturl != "https://www.baidu.com":
                    rm.updateRedis(real_key+"baidu",nexturl)
                    yield scrapy.Request(url=nexturl, callback=self.parse, meta={'cookiejar':response.meta['cookiejar'],'change_proxy':change_proxy,"keyword":response.request.meta["keyword"],'proxy':response.request.meta["proxy"]},headers=BAIDU_HEADERS)
                
        except Exception as e:
            print 'xxxxxxxxxxxxxx'
            print e
     