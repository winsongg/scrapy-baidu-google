# -*- coding: utf-8 -*-
import scrapy
from googleprj.items import DmozItem,gurl
from lxml import etree
import re,time
import urllib
import requests
from googleprj.settings import *
from googleprj.redisM import RedisM
import MySQLdb

count = 0
rm = RedisM()
db = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB)
cursor = db.cursor()
params = {"Home & Kitchen":["1055398","1248816011","1248915011"],"Beauty & Personal Care":["3760911","1248798011","1248873011"],\
          "Electronics":["172282","1248801011","1248879011"],"Health, Household & Baby Care":["3760901","1248810011","1248903011"],\
          "Pet Supplies":["2619533011","2661601011","2661618011"],"Tools & Home Improvement":["228013","1248813011","1248909011"],\
          "Office Products":["1064954","1248831011","1248945011"]}  #{"bigname":["id","include","star"]"}

class amazon(scrapy.Spider):
    
    name = "amazonsearch"
    allowed_domains = ["amazon.com"]
    
    def start_requests(self):
        global rm,cursor,db
        if rm.getvalue("amazonpool") == None or len(rm.getvalue("amazonpool"))<5:
            rm.pushredis("amazonpool",IPPOOL)
            
        sql = "select bigname,keyword from tb_keywords where isvalid=1 and bigname!='Clothing, Shoes & Jewelry'"
        key = "search_keypool"
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            if rm.getvalue(key) == None or len(rm.getvalue(key))==0:
                rm.pushredis(key,results)
        except Exception,e:
            print e
        
        while rm.getvalue(key) != None and len(rm.getvalue(key))!=0:
            dict = eval(rm.popredis(key,"search_dealpool"))
            keyword = dict[1].replace("&","%26")
            start_url = "https://www.amazon.com/s/s/ref=sr_nr_p_n_availability_1?rh=n:"+params[dict[0]][0]+",k:"+keyword+",p_72:"+params[dict[0]][2]+",p_n_availability:"+params[dict[0]][1]+"&keywords="+keyword+"&ie=UTF8"
            print 'start------------url:'+start_url
            yield scrapy.Request(url=start_url, callback=self.parse,headers=AMAZON_HEADERS,meta={'cookiejar':1})
    
    def parse(self, response):
        global count,rm,cursor,db
        count += 1
        #填充IP池
        if rm.getvalue("amazonpool") == None or len(rm.getvalue("amazonpool"))<5:
            rm.pushredis("amazonpool",IPPOOL)
        
        #判断是否大于300页的
        if(len(response.xpath('//span[@class="pagnDisabled"]')))>0:
            if int(response.xpath('//span[@class="pagnDisabled"]/text()')[0].extract())>=400:
                return
            
        if(len(response.xpath('//ul[@id="s-results-list-atf"]')))>0:
            lis = response.xpath('//ul[@id="s-results-list-atf"]/li')
            for li in lis:
                flag = False
                check = li.xpath("//span[@class='a-size-small a-color-secondary']")[0].extract()  
                
                if "Currently unavailable" in check:
                    flag = True
                
                if flag == True:
                    url = li.xpath("div/div[3]/div[1]/a/@href")[0].extract()  
                    requesturl = response.request.url
                    start = requesturl.find("keywords=")
                    end = requesturl.find("&ie=UTF8")
                    keyword = requesturl[start+9:end]
                    print keyword
                    item = gurl()
                    item['url'] =  url
                    item['keyword'] = keyword.replace("+"," ").replace("%26","&").replace("%27","")
                    item['isvalid'] = 1
                    yield item
                
        change_proxy = False
        title = None
        if len(response.xpath('//title/text()'))>0:
            title = response.xpath('//title/text()')[0].extract()
        body = response.body
        dogimg = response.xpath('//*[@id="d"]')
        if title != None and ("Robot Check" in title or "503" in title or "service un" in title.lower()):
            change_proxy = True
        elif (dogimg != None and len(dogimg)>0) or '._TTD_.jpg' in body :
            change_proxy = True
        
        nexturl = "https://www.amazon.com"
        nextpages = response.xpath('//*[@id="pagnNextLink"]') 
        if len(nextpages.xpath("@href"))>0:
            nexturl += nextpages.xpath("@href")[0].extract()
        print "nexturl:"+nexturl
        if nexturl != "https://www.amazon.com":
            yield scrapy.Request(url=nexturl, callback=self.parse, meta={'cookiejar':response.meta['cookiejar'],'change_proxy':change_proxy,'proxy':response.request.meta["proxy"]},headers=AMAZON_HEADERS)
            
        '''
        key = "search_"+time.strftime("%d%m%Y")
        if len(rm.getvalue(key))>0:
            dict = eval(rm.popredis(key,"amazon_dealpool"))
            print dict[0]
            yield scrapy.Request(url=dict[0], callback=self.parse, meta={'cookiejar':response.meta['cookiejar'],'change_proxy':change_proxy,'proxy':response.request.meta["proxy"]},headers=AMAZON_HEADERS)
        '''