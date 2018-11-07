# -*- coding: utf-8 -*-
import scrapy
from googleprj.items import DmozItem,gurl
from lxml import etree
import re
import urllib
import requests
from googleprj.settings import *
from googleprj.redisM import RedisM
import MySQLdb

db = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB)
cursor = db.cursor()
rm = RedisM()

class google(scrapy.Spider):
    name = "googleurl"
    allowed_domains = ["google.com","google.com.hk"]
    
    def start_requests(self):
        #填充IP池
        if rm.getvalue("googlepool") == None or len(rm.getvalue("googlepool"))<5:
            rm.pushredis("googlepool",IPPOOL)
        
        #填充google要爬的关键词
        if rm.getvalue("googlekeyword") == None or len(rm.getvalue("googlekeyword"))==0:
            sql = "select keyword from tb_keywords where isvalid=1"
            cursor.execute(sql)
            keywords = cursor.fetchall()
            kk = []
            for row in keywords:
                kk.append(row[0])
            print kk
            rm.pushredis("googlekeyword",kk)
        
        key = rm.popredis("googlekeyword","googlekeyword_dealpool")
        
        print key
        #check if exist last url
        last = rm.checkExist(key)
        if last == None:
                print 'first start 11111111'
                url = 'https://www.google.com/search?q=site%3Aamazon.com+'+key.replace(" ", "+").replace("&","%26")+'+currently+unavailable&oq=site%3Aamazon.com+'+key.replace(" ", "+").replace("&","%26")+'+currently+unavailable&aqs=chrome..69i57j69i58j69i60.3924j0j8&sourceid=chrome&ie=UTF-8'
                yield scrapy.Request(url=url, callback=self.parse,headers=GOOGLE_HEADERS,meta={'cookiejar':1})
        else :
                url = last
                print 'second start 222222222'
                yield scrapy.Request(url=url, callback=self.parse,headers=GOOGLE_HEADERS,meta={'cookiejar':1})
        rm.close(key)
    
    def parse(self, response):
        
        #try:
            keytemp = ""
            list = response.xpath('//*[@id="rso"]/div/div/div')  
            change_proxy = False
            if list == None or len(list)<0:
                change_proxy = True
            for one in list:
                real_url = ""
                if len(one.xpath("div/div/h3/a/@href"))>0:
                    real_url = one.xpath("div/div/h3/a/@href")[0].extract()  
                if "https://www.amazon.com" in real_url or "http://amazon.com" in real_url:
                    keytemp = response.request.url
                    keytemp = keytemp[keytemp.find('amazon.com')+10:keytemp.find('currently')].replace("+"," ").replace("%27","").replace("%26","&").replace("'","")
                    keytemp = keytemp.strip()
                    item = gurl()
                    item['url'] =  real_url
                    item['keyword'] = keytemp
                    item['isvalid'] = 1
                    yield item
            
            rj = response.xpath('//*[@id="recaptcha-anchor-label"]/span')#进行人机身份验证
            if len(rj)>0:
                print rj.xpath("text()")[0].extract()
                yield scrapy.Request(url=nexturl, callback=self.parse, meta={'cookiejar':response.meta['cookiejar'],'change_proxy':True,'proxy':response.request.meta["proxy"]},headers=GOOGLE_HEADERS)
            else:
                nexturl = "https://www.google.com"
                nextpages = response.xpath('//*[@id="pnnext"]') 
                if len(nextpages.xpath("@href"))>0:
                        nexturl += nextpages.xpath("@href")[0].extract()
                print "nexturl:"+nexturl
                if nexturl != "https://www.google.com":
                    rm.updateRedis(keytemp,nexturl)
                    yield scrapy.Request(url=nexturl, callback=self.parse, meta={'cookiejar':response.meta['cookiejar'],'change_proxy':change_proxy,'proxy':response.request.meta["proxy"]},headers=GOOGLE_HEADERS)
        #except Exception as e:
        #    print 'xxxxxxxxxxxxxx'
        #    print e
                    